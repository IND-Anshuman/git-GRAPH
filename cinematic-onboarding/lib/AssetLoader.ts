// Task 1.14: Asset Loader - Progressive loading and IndexedDB caching of 3D assets

import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { DRACOLoader } from "three/examples/jsm/loaders/DRACOLoader.js";

export enum AssetPriority {
  CRITICAL = 0,
  HIGH = 1,
  LOW = 2,
}

interface QueueItem {
  url: string;
  type: "model" | "texture" | "audio";
  format: string;
  priority: AssetPriority;
  resolve: (value: any) => void;
  reject: (error: any) => void;
}

type ProgressCallback = (url: string, percentage: number) => void;

/**
 * AssetLoader class handles loading, preloading, and caching of 3D assets
 * (models, textures, audio) with IndexedDB support, exponential backoff
 * retries, priority queues, and granular progress updates.
 */
export class AssetLoader {
  private static instance: AssetLoader | null = null;

  private memoryCache: Map<string, any> = new Map();
  private db: IDBDatabase | null = null;
  private readonly dbName = "AssetCacheDB";
  private readonly storeName = "assets";
  private readonly dbVersion = 1;
  private readonly cacheVersion = "1.0.0"; // Version-based invalidation

  private queue: QueueItem[] = [];
  private activeConnections = 0;
  private readonly maxConcurrent = 3;

  private progressCallbacks: Set<ProgressCallback> = new Set();

  private constructor() {
    this.initDB();
  }

  /**
   * Returns the singleton instance of the AssetLoader.
   */
  static getInstance(): AssetLoader {
    if (!AssetLoader.instance) {
      AssetLoader.instance = new AssetLoader();
    }
    return AssetLoader.instance;
  }

  private initDB(): Promise<void> {
    return new Promise((resolve) => {
      if (typeof window === "undefined") {
        resolve();
        return;
      }

      const request = indexedDB.open(this.dbName, this.dbVersion);

      request.onupgradeneeded = () => {
        const db = request.result;
        if (!db.objectStoreNames.contains(this.storeName)) {
          db.createObjectStore(this.storeName, { keyPath: "url" });
        }
      };

      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onerror = () => {
        console.error("[AssetLoader] Failed to open IndexedDB", request.error);
        resolve(); // Degrade gracefully: proceed without DB cache
      };
    });
  }

  /**
   * Registers a callback to track loading progress.
   */
  onProgress(callback: ProgressCallback): () => void {
    this.progressCallbacks.add(callback);
    return () => {
      this.progressCallbacks.delete(callback);
    };
  }

  /**
   * Loads a 3D GLTF/GLB model, checking caches and retrying upon failure.
   */
  async loadModel(url: string, format: "gltf" | "glb", priority = AssetPriority.HIGH): Promise<any> {
    if (this.memoryCache.has(url)) {
      return this.memoryCache.get(url);
    }

    const cachedData = await this.readFromCache(url);
    if (cachedData) {
      try {
        const gltf = await this.parseModel(cachedData, url);
        this.memoryCache.set(url, gltf);
        return gltf;
      } catch (err) {
        console.warn(`[AssetLoader] Failed to parse cached model for ${url}, refetching...`, err);
      }
    }

    const responseBuffer = await this.enqueue(url, "model", format, priority);
    await this.writeToCache(url, responseBuffer);

    const gltf = await this.parseModel(responseBuffer, url);
    this.memoryCache.set(url, gltf);
    return gltf;
  }

  /**
   * Loads a texture, checking caches and retrying upon failure.
   */
  async loadTexture(url: string, format: "webp" | "basis", priority = AssetPriority.HIGH): Promise<THREE.Texture> {
    if (this.memoryCache.has(url)) {
      return this.memoryCache.get(url);
    }

    const cachedData = await this.readFromCache(url);
    if (cachedData) {
      try {
        const texture = await this.parseTexture(cachedData);
        this.memoryCache.set(url, texture);
        return texture;
      } catch (err) {
        console.warn(`[AssetLoader] Failed to parse cached texture for ${url}, refetching...`, err);
      }
    }

    const responseBuffer = await this.enqueue(url, "texture", format, priority);
    await this.writeToCache(url, responseBuffer);

    const texture = await this.parseTexture(responseBuffer);
    this.memoryCache.set(url, texture);
    return texture;
  }

  /**
   * Preloads a list of asset URLs with medium priority.
   */
  async preload(urls: string[]): Promise<void> {
    const promises = urls.map(async (url) => {
      const isModel = url.endsWith(".gltf") || url.endsWith(".glb");
      const format = url.endsWith(".glb") ? "glb" : (url.endsWith(".gltf") ? "gltf" : "webp");
      
      try {
        if (isModel) {
          await this.loadModel(url, format as any, AssetPriority.LOW);
        } else {
          await this.loadTexture(url, format as any, AssetPriority.LOW);
        }
      } catch (err) {
        console.error(`[AssetLoader] Preload failed for ${url}`, err);
      }
    });

    await Promise.all(promises);
  }

  /**
   * Checks if an asset is cached in memory.
   */
  isCached(url: string): boolean {
    return this.memoryCache.has(url);
  }

  /**
   * Clears memory cache and IndexedDB cache.
   */
  async clearCache(): Promise<void> {
    this.memoryCache.clear();
    
    if (typeof window === "undefined" || !this.db) return;

    return new Promise<void>((resolve) => {
      try {
        const tx = this.db!.transaction(this.storeName, "readwrite");
        const store = tx.objectStore(this.storeName);
        const req = store.clear();
        req.onsuccess = () => resolve();
        req.onerror = () => {
          console.warn("[AssetLoader] Failed to clear IndexedDB cache");
          resolve();
        };
      } catch {
        resolve();
      }
    });
  }

  private readFromCache(url: string): Promise<ArrayBuffer | null> {
    return new Promise((resolve) => {
      if (typeof window === "undefined" || !this.db) {
        resolve(null);
        return;
      }

      try {
        const tx = this.db.transaction(this.storeName, "readonly");
        const store = tx.objectStore(this.storeName);
        const request = store.get(url);

        request.onsuccess = () => {
          const result = request.result;
          if (result && result.version === this.cacheVersion) {
            resolve(result.data);
          } else {
            resolve(null); // Invalid or out-of-date cache
          }
        };

        request.onerror = () => resolve(null);
      } catch {
        resolve(null);
      }
    });
  }

  private writeToCache(url: string, data: ArrayBuffer): Promise<void> {
    return new Promise<void>((resolve) => {
      if (typeof window === "undefined" || !this.db) {
        resolve();
        return;
      }

      try {
        const tx = this.db.transaction(this.storeName, "readwrite");
        const store = tx.objectStore(this.storeName);
        store.put({
          url,
          data,
          version: this.cacheVersion,
          timestamp: Date.now(),
        });
        tx.oncomplete = () => resolve();
        tx.onerror = () => resolve();
      } catch {
        resolve();
      }
    });
  }

  private enqueue(url: string, type: "model" | "texture" | "audio", format: string, priority: AssetPriority): Promise<ArrayBuffer> {
    return new Promise((resolve, reject) => {
      const item: QueueItem = { url, type, format, priority, resolve, reject };
      this.queue.push(item);
      this.queue.sort((a, b) => a.priority - b.priority); // Sort so CRITICAL/HIGH are processed first
      this.processQueue();
    });
  }

  private processQueue(): void {
    if (this.activeConnections >= this.maxConcurrent || this.queue.length === 0) {
      return;
    }

    const item = this.queue.shift()!;
    this.activeConnections++;

    this.fetchWithRetry(item.url)
      .then((buffer) => {
        this.activeConnections--;
        item.resolve(buffer);
        this.processQueue();
      })
      .catch((err) => {
        this.activeConnections--;
        item.reject(err);
        this.processQueue();
      });
  }

  private async fetchWithRetry(url: string, retries = 3, delay = 2000): Promise<ArrayBuffer> {
    let lastError: any;
    
    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Setup progress tracking if supported
        if (response.body) {
          const reader = response.body.getReader();
          const contentLength = +(response.headers.get("Content-Length") ?? 0);
          
          let receivedLength = 0;
          const chunks: Uint8Array[] = [];

          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            chunks.push(value);
            receivedLength += value.length;

            if (contentLength > 0) {
              const percentage = (receivedLength / contentLength) * 100;
              this.notifyProgress(url, percentage);
            }
          }

          // Combine chunks into a single ArrayBuffer
          const combined = new Uint8Array(receivedLength);
          let position = 0;
          for (const chunk of chunks) {
            combined.set(chunk, position);
            position += chunk.length;
          }
          
          this.notifyProgress(url, 100);
          return combined.buffer;
        } else {
          // Fallback if body reader is unavailable
          this.notifyProgress(url, 50);
          const buf = await response.arrayBuffer();
          this.notifyProgress(url, 100);
          return buf;
        }
      } catch (err: any) {
        lastError = err;
        console.warn(`[AssetLoader] Fetch attempt ${attempt} failed for ${url}. Error: ${err.message}`);
        
        if (attempt < retries) {
          // Exponential backoff delay (2s, 4s, 8s...)
          const actualDelay = delay * Math.pow(2, attempt - 1);
          await new Promise((resolve) => setTimeout(resolve, actualDelay));
        }
      }
    }

    throw new Error(`Failed to load asset ${url} after ${retries} attempts. Last error: ${lastError.message}`);
  }

  private notifyProgress(url: string, percentage: number): void {
    this.progressCallbacks.forEach((cb) => {
      try {
        cb(url, percentage);
      } catch (err) {
        console.error("[AssetLoader] Error in progress callback", err);
      }
    });
  }

  private parseModel(buffer: ArrayBuffer, url: string): Promise<any> {
    return new Promise((resolve, reject) => {
      const loader = new GLTFLoader();
      const dracoLoader = new DRACOLoader();
      
      // Setup Draco decoders CDN path
      dracoLoader.setDecoderPath("https://www.gstatic.com/draco/versioned/decoders/1.5.5/");
      loader.setDRACOLoader(dracoLoader);

      loader.parse(
        buffer,
        url,
        (gltf) => {
          dracoLoader.dispose();
          resolve(gltf);
        },
        (error) => {
          dracoLoader.dispose();
          reject(error);
        }
      );
    });
  }

  private parseTexture(buffer: ArrayBuffer): Promise<THREE.Texture> {
    return new Promise((resolve, reject) => {
      const blob = new Blob([buffer]);
      const blobUrl = URL.createObjectURL(blob);
      const loader = new THREE.TextureLoader();

      loader.load(
        blobUrl,
        (texture) => {
          URL.revokeObjectURL(blobUrl);
          resolve(texture);
        },
        undefined,
        (error) => {
          URL.revokeObjectURL(blobUrl);
          reject(error);
        }
      );
    });
  }
}
