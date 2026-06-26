// Task 3.6: Texture Atlasing - Packs all particle textures into a single atlas

import * as THREE from "three";

export interface TextureAtlasEntry {
  name: string;
  uvOffset: [number, number];
  uvSize: [number, number];
}

/**
 * TextureAtlasManager class handles loading of the texture atlas image and manifest file,
 * and yields UV transformations (offset, scale) to map sub-textures inside shaders.
 */
export class TextureAtlasManager {
  private static instance: TextureAtlasManager | null = null;
  private atlas: THREE.Texture | null = null;
  private entries: Map<string, TextureAtlasEntry> = new Map();

  private constructor() {}

  /**
   * Returns the singleton instance of TextureAtlasManager.
   */
  static getInstance(): TextureAtlasManager {
    if (!TextureAtlasManager.instance) {
      TextureAtlasManager.instance = new TextureAtlasManager();
    }
    return TextureAtlasManager.instance;
  }

  /**
   * Loads the texture atlas image and manifest coordinates file.
   */
  async loadAtlas(atlasPath: string, manifestPath: string): Promise<void> {
    try {
      // 1. Fetch manifest
      const response = await fetch(manifestPath);
      if (!response.ok) {
        throw new Error(`Failed to load atlas manifest: HTTP ${response.status}`);
      }
      const manifest = await response.json();
      
      this.entries.clear();
      if (Array.isArray(manifest.entries)) {
        manifest.entries.forEach((entry: TextureAtlasEntry) => {
          this.entries.set(entry.name, entry);
        });
      } else if (manifest.entries) {
        Object.keys(manifest.entries).forEach((key) => {
          this.entries.set(key, {
            name: key,
            uvOffset: manifest.entries[key].uvOffset,
            uvSize: manifest.entries[key].uvSize,
          });
        });
      }

      // 2. Load texture
      const loader = new THREE.TextureLoader();
      this.atlas = await new Promise<THREE.Texture>((resolve, reject) => {
        loader.load(
          atlasPath,
          (texture) => resolve(texture),
          undefined,
          (err) => reject(err)
        );
      });
      
      console.log(`[TextureAtlasManager] Atlas loaded successfully: ${this.entries.size} sub-textures`);
    } catch (err) {
      console.error("[TextureAtlasManager] Error loading texture atlas", err);
      throw err;
    }
  }

  /**
   * Returns the UV transformation parameters for a named sub-texture.
   */
  getUVTransform(textureName: string): { offset: THREE.Vector2; scale: THREE.Vector2 } {
    const entry = this.entries.get(textureName);
    if (!entry) {
      // Fallback to standard full texture bounds
      return {
        offset: new THREE.Vector2(0, 0),
        scale: new THREE.Vector2(1, 1),
      };
    }
    return {
      offset: new THREE.Vector2(entry.uvOffset[0], entry.uvOffset[1]),
      scale: new THREE.Vector2(entry.uvSize[0], entry.uvSize[1]),
    };
  }

  /**
   * Returns the loaded atlas texture.
   */
  getAtlasTexture(): THREE.Texture | null {
    return this.atlas;
  }
}
