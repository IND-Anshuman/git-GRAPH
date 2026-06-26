import * as THREE from "three";
import { useOnboardingStore } from "@/stores/onboardingStore";

export interface OctreeItem {
  id: string;
  position: THREE.Vector3;
  radius: number;
  metadata: any;
}

export class BoundingBox {
  min: THREE.Vector3;
  max: THREE.Vector3;

  constructor(min: THREE.Vector3, max: THREE.Vector3) {
    this.min = min.clone();
    this.max = max.clone();
  }

  contains(point: THREE.Vector3): boolean {
    return (
      point.x >= this.min.x && point.x <= this.max.x &&
      point.y >= this.min.y && point.y <= this.max.y &&
      point.z >= this.min.z && point.z <= this.max.z
    );
  }

  intersectsRay(ray: THREE.Ray): boolean {
    let tmin = (this.min.x - ray.origin.x) / (ray.direction.x || 0.000001);
    let tmax = (this.max.x - ray.origin.x) / (ray.direction.x || 0.000001);
    if (tmin > tmax) [tmin, tmax] = [tmax, tmin];

    let tymin = (this.min.y - ray.origin.y) / (ray.direction.y || 0.000001);
    let tymax = (this.max.y - ray.origin.y) / (ray.direction.y || 0.000001);
    if (tmin > tymax || tymin > tmax) return false;
    if (tymin > tmin) tmin = tymin;
    if (tymax < tmax) tmax = tymax;

    let tzmin = (this.min.z - ray.origin.z) / (ray.direction.z || 0.000001);
    let tzmax = (this.max.z - ray.origin.z) / (ray.direction.z || 0.000001);
    if (tmin > tzmax || tzmin > tmax) return false;
    return true;
  }
}

export class OctreeNode {
  boundary: BoundingBox;
  capacity: number;
  items: OctreeItem[] = [];
  children: OctreeNode[] | null = null;
  depth: number;

  constructor(boundary: BoundingBox, capacity: number = 32, depth: number = 0) {
    this.boundary = boundary;
    this.capacity = capacity;
    this.depth = depth;
  }

  subdivide(): void {
    const min = this.boundary.min;
    const max = this.boundary.max;
    const mid = new THREE.Vector3().addVectors(min, max).multiplyScalar(0.5);

    this.children = [];
    for (let x = 0; x < 2; x++) {
      for (let y = 0; y < 2; y++) {
        for (let z = 0; z < 2; z++) {
          const subMin = new THREE.Vector3(
            x === 0 ? min.x : mid.x,
            y === 0 ? min.y : mid.y,
            z === 0 ? min.z : mid.z
          );
          const subMax = new THREE.Vector3(
            x === 0 ? mid.x : max.x,
            y === 0 ? mid.y : max.y,
            z === 0 ? mid.z : max.z
          );
          const box = new BoundingBox(subMin, subMax);
          this.children.push(new OctreeNode(box, this.capacity, this.depth + 1));
        }
      }
    }

    for (const item of this.items) {
      this.insertIntoChildren(item);
    }
    this.items = [];
  }

  private insertIntoChildren(item: OctreeItem): boolean {
    if (!this.children) return false;
    for (const child of this.children) {
      if (child.boundary.contains(item.position)) {
        child.insert(item);
        return true;
      }
    }
    this.children[0].insert(item);
    return true;
  }

  insert(item: OctreeItem): boolean {
    if (!this.boundary.contains(item.position)) {
      return false;
    }

    if (this.children) {
      return this.insertIntoChildren(item);
    }

    this.items.push(item);

    if (this.items.length > this.capacity && this.depth < 6) {
      this.subdivide();
    }

    return true;
  }

  queryRay(ray: THREE.Ray, maxDistance: number, results: OctreeItem[]): void {
    if (!this.boundary.intersectsRay(ray)) {
      return;
    }

    if (this.children) {
      for (const child of this.children) {
        child.queryRay(ray, maxDistance, results);
      }
    } else {
      for (const item of this.items) {
        const dist = ray.distanceToPoint(item.position);
        if (dist < maxDistance + item.radius) {
          results.push(item);
        }
      }
    }
  }
}

/**
 * Centralized InteractionHandler class manages raycasting and keyboard events.
 * It uses an Octree spatial index to achieve O(log N) raycast complexity on 30k+ points.
 */
export class InteractionHandler {
  private static instance: InteractionHandler | null = null;
  private registry: Map<string, OctreeItem> = new Map();
  private rootNode: OctreeNode | null = null;
  private lastRaycastTime: number = 0;
  
  // Accessibility Focus List
  private focusList: string[] = [];
  private focusIndex: number = -1;

  private constructor() {}

  static getInstance(): InteractionHandler {
    if (!InteractionHandler.instance) {
      InteractionHandler.instance = new InteractionHandler();
    }
    return InteractionHandler.instance;
  }

  registerObject(id: string, position: [number, number, number] | THREE.Vector3, radius: number, metadata: any): void {
    const pos = position instanceof THREE.Vector3 ? position.clone() : new THREE.Vector3(...position);
    this.registry.set(id, { id, position: pos, radius, metadata });
    this.rebuildOctree();
  }

  unregisterObject(id: string): void {
    if (this.registry.delete(id)) {
      this.rebuildOctree();
    }
  }

  clearRegistry(): void {
    this.registry.clear();
    this.rootNode = null;
    this.focusList = [];
    this.focusIndex = -1;
  }

  private rebuildOctree(): void {
    const items = Array.from(this.registry.values());
    if (items.length === 0) {
      this.rootNode = null;
      this.focusList = [];
      this.focusIndex = -1;
      return;
    }

    // Determine spatial bounding box of all items
    const min = new THREE.Vector3(Infinity, Infinity, Infinity);
    const max = new THREE.Vector3(-Infinity, -Infinity, -Infinity);

    items.forEach((item) => {
      min.min(item.position);
      max.max(item.position);
    });

    // Expand bounding box slightly to avoid edge containment issues
    min.subScalar(2.0);
    max.addScalar(2.0);

    const rootBox = new BoundingBox(min, max);
    this.rootNode = new OctreeNode(rootBox, 32, 0);

    items.forEach((item) => {
      this.rootNode!.insert(item);
    });

    // Re-generate logical tab-order based on coordinates (sorted by Z coordinate for scene depth flow)
    this.focusList = items
      .sort((a, b) => a.position.z - b.position.z)
      .map((item) => item.id);
      
    // Clamp focus index if out of bounds
    if (this.focusIndex >= this.focusList.length) {
      this.focusIndex = this.focusList.length - 1;
    }
  }

  /**
   * Raycast handler throttled to 60ms to maintain solid 60 FPS under mouse moves
   */
  raycast(camera: THREE.Camera, mouseCoords: THREE.Vector2): OctreeItem | null {
    if (!this.rootNode) return null;

    const now = performance.now();
    if (now - this.lastRaycastTime < 60) {
      // Return previous state (throttled)
      const store = useOnboardingStore.getState();
      const currentHovered = store.hoveredObjectId;
      return currentHovered ? this.registry.get(currentHovered) ?? null : null;
    }
    this.lastRaycastTime = now;

    // Perform standard R3F Raycaster setup
    const raycaster = new THREE.Raycaster();
    raycaster.setFromCamera(mouseCoords, camera);

    // Query octree for close points
    const hits: OctreeItem[] = [];
    this.rootNode.queryRay(raycaster.ray, 3.5, hits);

    if (hits.length === 0) {
      useOnboardingStore.getState().setHoveredObject(null);
      return null;
    }

    // Sort hits along ray distance
    hits.sort((a, b) => {
      const distA = raycaster.ray.origin.distanceToSquared(a.position);
      const distB = raycaster.ray.origin.distanceToSquared(b.position);
      return distA - distB;
    });

    const closestHit = hits[0];
    useOnboardingStore.getState().setHoveredObject(closestHit.id);
    return closestHit;
  }

  /**
   * Triggers keyboard navigation (Tab focus cycling)
   */
  handleKeyDown(event: KeyboardEvent): void {
    if (this.focusList.length === 0) return;

    const store = useOnboardingStore.getState();

    // Tab key: navigate focus
    if (event.key === "Tab") {
      event.preventDefault();
      if (event.shiftKey) {
        // Shift + Tab: reverse focus
        this.focusIndex = this.focusIndex <= 0 ? this.focusList.length - 1 : this.focusIndex - 1;
      } else {
        // Tab: forward focus
        this.focusIndex = this.focusIndex >= this.focusList.length - 1 ? 0 : this.focusIndex + 1;
      }

      const activeId = this.focusList[this.focusIndex];
      store.setFocusedObject(activeId);
      store.setHoveredObject(activeId); // highlight item
    }

    // Enter / Space: activate selected
    if (event.key === "Enter" || event.key === " ") {
      const activeId = store.focusedObjectId || store.hoveredObjectId;
      if (activeId) {
        event.preventDefault();
        store.expandCard(activeId);
      }
    }

    // Escape: close detail panel
    if (event.key === "Escape") {
      if (store.expandedCardId) {
        event.preventDefault();
        store.closeCard();
      }
    }
  }

  getObjectMetadata(id: string): any {
    return this.registry.get(id)?.metadata;
  }
}
