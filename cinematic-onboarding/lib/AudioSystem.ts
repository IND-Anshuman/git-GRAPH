import * as THREE from "three";
import gsap from "gsap";

/**
 * Procedural Audio System using the Web Audio API
 * Generates ambient drones, scene whooshes, spatial pulses, hovers, and clicks programmatically.
 */
export class AudioSystem {
  private static instance: AudioSystem | null = null;
  private context: AudioContext | null = null;
  
  // Volume and state settings
  private masterGain: GainNode | null = null;
  private ambientGain: GainNode | null = null;
  private isEnabled: boolean = false;
  private volume: number = 0.5;

  // Nodes for ambient synth loop
  private ambientOscs: OscillatorNode[] = [];
  private ambientFilter: BiquadFilterNode | null = null;
  private ambientLFO: OscillatorNode | null = null;
  private noiseBuffer: AudioBuffer | null = null;

  private constructor() {
    if (typeof window !== "undefined") {
      // Load preference from localStorage
      this.isEnabled = localStorage.getItem("sip-audio-enabled") === "true";
      this.volume = Number(localStorage.getItem("sip-audio-volume") ?? "0.5");
    }
  }

  static getInstance(): AudioSystem {
    if (!AudioSystem.instance) {
      AudioSystem.instance = new AudioSystem();
    }
    return AudioSystem.instance;
  }

  /**
   * Initializes the AudioContext on first user gesture (autoplay compliant)
   */
  initContext(): void {
    if (this.context || typeof window === "undefined") return;

    const AudioCtxClass = window.AudioContext || (window as any).webkitAudioContext;
    this.context = new AudioCtxClass();

    // Create master gain
    this.masterGain = this.context.createGain();
    this.masterGain.gain.setValueAtTime(this.volume, this.context.currentTime);
    this.masterGain.connect(this.context.destination);

    // Create ambient gain
    this.ambientGain = this.context.createGain();
    this.ambientGain.gain.setValueAtTime(0.0, this.context.currentTime); // start silent
    this.ambientGain.connect(this.masterGain);

    // Build procedural white noise buffer for whooshes
    const bufferSize = this.context.sampleRate * 2; // 2 seconds
    this.noiseBuffer = this.context.createBuffer(1, bufferSize, this.context.sampleRate);
    const output = this.noiseBuffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      output[i] = Math.random() * 2.0 - 1.0;
    }

    if (this.isEnabled) {
      this.startAmbient();
    }
  }

  setEnabled(enabled: boolean): void {
    this.isEnabled = enabled;
    if (typeof window !== "undefined") {
      localStorage.setItem("sip-audio-enabled", String(enabled));
    }

    if (enabled) {
      this.initContext();
      if (this.context?.state === "suspended") {
        this.context.resume();
      }
      this.startAmbient();
    } else {
      this.stopAmbient();
    }
  }

  getEnabled(): boolean {
    return this.isEnabled;
  }

  setVolume(vol: number): void {
    this.volume = vol;
    if (typeof window !== "undefined") {
      localStorage.setItem("sip-audio-volume", String(vol));
    }
    if (this.masterGain && this.context) {
      this.masterGain.gain.setValueAtTime(vol, this.context.currentTime);
    }
  }

  getVolume(): number {
    return this.volume;
  }

  /**
   * Procedural Space Drone synthesis (using detuned saw waves + slow LFO cutoff sweeps)
   */
  private startAmbient(): void {
    if (!this.context || !this.ambientGain || this.ambientOscs.length > 0) return;

    const ctx = this.context;

    // 1. Create a low-pass filter
    this.ambientFilter = ctx.createBiquadFilter();
    this.ambientFilter.type = "lowpass";
    this.ambientFilter.frequency.setValueAtTime(120, ctx.currentTime);
    this.ambientFilter.Q.setValueAtTime(3.0, ctx.currentTime);
    this.ambientFilter.connect(this.ambientGain);

    // 2. Create detuned base oscillators (Cosmic Drone)
    const baseFreqs = [55.0, 55.4, 110.0, 110.8]; // detuned A1 and A2
    baseFreqs.forEach((freq, idx) => {
      const osc = ctx.createOscillator();
      osc.type = idx % 2 === 0 ? "sawtooth" : "triangle";
      osc.frequency.setValueAtTime(freq, ctx.currentTime);

      const oscGain = ctx.createGain();
      oscGain.gain.setValueAtTime(0.08, ctx.currentTime); // keep individual oscillators quiet

      osc.connect(oscGain);
      oscGain.connect(this.ambientFilter!);
      osc.start();

      this.ambientOscs.push(osc);
    });

    // 3. Create slow LFO to sweep filter cutoff frequency
    this.ambientLFO = ctx.createOscillator();
    this.ambientLFO.type = "sine";
    this.ambientLFO.frequency.setValueAtTime(0.08, ctx.currentTime); // 0.08 Hz = ~12s sweep

    const lfoGain = ctx.createGain();
    lfoGain.gain.setValueAtTime(80, ctx.currentTime); // Sweep depth +/- 80Hz

    this.ambientLFO.connect(lfoGain);
    lfoGain.connect(this.ambientFilter.frequency);
    this.ambientLFO.start();

    // Smoothly fade in ambient sound over 2 seconds
    this.ambientGain.gain.cancelScheduledValues(ctx.currentTime);
    this.ambientGain.gain.setValueAtTime(0.0, ctx.currentTime);
    this.ambientGain.gain.linearRampToValueAtTime(0.5, ctx.currentTime + 2.0);
  }

  private stopAmbient(): void {
    // Fade out ambient gain over 0.5s before stopping oscillators
    if (this.ambientGain && this.context) {
      const ctx = this.context;
      this.ambientGain.gain.cancelScheduledValues(ctx.currentTime);
      this.ambientGain.gain.linearRampToValueAtTime(0.0, ctx.currentTime + 0.5);

      setTimeout(() => {
        if (this.ambientOscs.length > 0) {
          this.ambientOscs.forEach(o => {
            try { o.stop(); } catch {}
          });
          this.ambientOscs = [];
        }
        if (this.ambientLFO) {
          try { this.ambientLFO.stop(); } catch {}
          this.ambientLFO = null;
        }
        this.ambientFilter = null;
      }, 600);
    }
  }

  /**
   * Synthesize a pitch/filter-swept Whoosh for scene transitions
   */
  playWhoosh(): void {
    if (!this.isEnabled || !this.context || !this.masterGain || !this.noiseBuffer) return;

    const ctx = this.context;
    const now = ctx.currentTime;

    // 1. Noise Source
    const noiseSource = ctx.createBufferSource();
    noiseSource.buffer = this.noiseBuffer;

    // 2. Whoosh Filter (Bandpass sweep)
    const filter = ctx.createBiquadFilter();
    filter.type = "bandpass";
    filter.Q.setValueAtTime(2.0, now);
    filter.frequency.setValueAtTime(80, now);
    filter.frequency.exponentialRampToValueAtTime(1800, now + 0.45);
    filter.frequency.exponentialRampToValueAtTime(150, now + 1.1);

    // 3. Whoosh Gain Envelope
    const gainNode = ctx.createGain();
    gainNode.gain.setValueAtTime(0.0, now);
    gainNode.gain.linearRampToValueAtTime(0.35, now + 0.35);
    gainNode.gain.exponentialRampToValueAtTime(0.001, now + 1.2);

    noiseSource.connect(filter);
    filter.connect(gainNode);
    gainNode.connect(this.masterGain);

    noiseSource.start(now);
    noiseSource.stop(now + 1.2);
  }

  /**
   * Synthesizes a crisp electronic blip on hovering interactive nodes
   */
  playHover(freq: number = 440): void {
    if (!this.isEnabled || !this.context || !this.masterGain) return;

    const ctx = this.context;
    const now = ctx.currentTime;

    const osc = ctx.createOscillator();
    osc.type = "sine";
    osc.frequency.setValueAtTime(freq, now);
    // Pitch slide downwards
    osc.frequency.exponentialRampToValueAtTime(freq * 0.5, now + 0.12);

    const gainNode = ctx.createGain();
    gainNode.gain.setValueAtTime(0.12, now);
    gainNode.gain.exponentialRampToValueAtTime(0.001, now + 0.12);

    osc.connect(gainNode);
    gainNode.connect(this.masterGain);

    osc.start(now);
    osc.stop(now + 0.13);
  }

  /**
   * Synthesizes a major third detuned chime on clicking nodes to confirm selection
   */
  playClick(): void {
    if (!this.isEnabled || !this.context || !this.masterGain) return;

    const ctx = this.context;
    const now = ctx.currentTime;

    const notes = [523.25, 659.25, 783.99]; // C5, E5, G5 major triad

    notes.forEach((freq, idx) => {
      const osc = ctx.createOscillator();
      osc.type = "triangle";
      osc.frequency.setValueAtTime(freq, now + idx * 0.03); // staggered arpeggio

      const filter = ctx.createBiquadFilter();
      filter.type = "lowpass";
      filter.frequency.setValueAtTime(1500, now);

      const gainNode = ctx.createGain();
      gainNode.gain.setValueAtTime(0.0, now);
      gainNode.gain.linearRampToValueAtTime(0.15, now + idx * 0.03 + 0.02);
      gainNode.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.03 + 0.4);

      osc.connect(filter);
      filter.connect(gainNode);
      gainNode.connect(this.masterGain!);

      osc.start(now);
      osc.stop(now + 0.5);
    });
  }

  /**
   * Synthesizes a spatialized pulse sound (used for reasoning flow sparks in 3D space)
   */
  playSpatialPulse(position: THREE.Vector3 | [number, number, number]): void {
    if (!this.isEnabled || !this.context || !this.masterGain) return;

    const ctx = this.context;
    const now = ctx.currentTime;

    // Create 3D Panner Node
    const panner = ctx.createPanner();
    panner.panningModel = "HRTF";
    panner.distanceModel = "inverse";
    panner.refDistance = 15;
    panner.maxDistance = 1000;
    panner.rolloffFactor = 1.0;

    const pos = position instanceof THREE.Vector3 ? position : new THREE.Vector3(...position);
    panner.positionX.value = pos.x;
    panner.positionY.value = pos.y;
    panner.positionZ.value = pos.z;

    const osc = ctx.createOscillator();
    osc.type = "sine";
    osc.frequency.setValueAtTime(880, now);
    osc.frequency.exponentialRampToValueAtTime(440, now + 0.2);

    const gainNode = ctx.createGain();
    gainNode.gain.setValueAtTime(0.2, now);
    gainNode.gain.exponentialRampToValueAtTime(0.001, now + 0.25);

    osc.connect(panner);
    panner.connect(gainNode);
    gainNode.connect(this.masterGain);

    osc.start(now);
    osc.stop(now + 0.26);
  }

  /**
   * Synchronizes the Web Audio spatial listener with the R3F Camera
   */
  updateListener(camera: THREE.Camera): void {
    if (!this.context) return;

    const listener = this.context.listener;
    
    // Extract camera world position, orientation, and up vector
    const camPosition = new THREE.Vector3();
    const camQuaternion = new THREE.Quaternion();
    const camScale = new THREE.Vector3();
    camera.matrixWorld.decompose(camPosition, camQuaternion, camScale);

    const orientation = new THREE.Vector3(0, 0, -1).applyQuaternion(camQuaternion);
    const up = new THREE.Vector3(0, 1, 0).applyQuaternion(camQuaternion);

    if (listener.positionX) {
      // Modern Web Audio API setting (Firefox/Chrome/Safari support)
      listener.positionX.value = camPosition.x;
      listener.positionY.value = camPosition.y;
      listener.positionZ.value = camPosition.z;
      listener.forwardX.value = orientation.x;
      listener.forwardY.value = orientation.y;
      listener.forwardZ.value = orientation.z;
      listener.upX.value = up.x;
      listener.upY.value = up.y;
      listener.upZ.value = up.z;
    } else {
      // Legacy Web Audio API fallback (for compatibility)
      try {
        (listener as any).setPosition(camPosition.x, camPosition.y, camPosition.z);
        (listener as any).setOrientation(orientation.x, orientation.y, orientation.z, up.x, up.y, up.z);
      } catch (err) {
        console.warn("[AudioSystem] Legacy listener positioning failed:", err);
      }
    }
  }

  /**
   * Smoothly adjusts the ambient gain level according to scene activity
   */
  adjustVolumeForScene(sceneNumber: number): void {
    if (!this.isEnabled || !this.ambientGain || !this.context) return;

    const intensityMap: Record<number, number> = {
      1: 0.25, // Chaos - quiet/ambient
      2: 0.65, // Stardust - slightly louder
      3: 0.45, // Constellation
      4: 0.40, // Planets
      5: 0.55, // Solar systems
      6: 0.45, // Decision rings
      7: 0.60, // Reasoning network
      8: 0.50  // Universe
    };

    const targetGain = intensityMap[sceneNumber] ?? 0.5;

    // Use GSAP to smoothly transition the ambient synth gain uniform over 1.5 seconds
    gsap.to(this.ambientGain.gain, {
      value: targetGain * 0.8, // scale factor
      duration: 1.5,
      ease: "power2.out",
      overwrite: "auto"
    });
  }
}
