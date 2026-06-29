// Task 3.2: GPU Shaders - Custom vertex and fragment shaders for GPU particle animations

const simplexNoiseGLSL = `
vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec4 permute(vec4 x) { return mod289(((x*34.0)+1.0)*x); }
vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }

float snoise(vec3 v) {
  const vec2 C = vec2(1.0/6.0, 1.0/3.0);
  const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);

  vec3 i  = floor(v + dot(v, C.yyy) );
  vec3 x0 =   v - i + dot(i, C.xxx) ;

  vec3 g = step(x0.yzx, x0.xyz);
  vec3 l = 1.0 - g;
  vec3 i1 = min( g.xyz, l.zxy );
  vec3 i2 = max( g.xyz, l.zxy );

  vec3 x1 = x0 - i1 + C.xxx;
  vec3 x2 = x0 - i2 + C.yyy;
  vec3 x3 = x0 - D.yyy;

  i = mod289(i);
  vec4 p = permute( permute( permute(
             i.z + vec4(0.0, i1.z, i2.z, 1.0) )
           + i.y + vec4(0.0, i1.y, i2.y, 1.0) )
           + i.x + vec4(0.0, i1.x, i2.x, 1.0) );

  float n_ = 0.142857142857; // 1.0/7.0
  vec3  ns = n_ * D.wyz - D.xzx;

  vec4 j = p - 49.0 * floor(p * ns.z);

  vec4 x_ = floor(j * ns.z);
  vec4 y_ = floor(j - 7.0 * x_ );

  vec4 x = x_ *ns.x + ns.yyyy;
  vec4 y = y_ *ns.x + ns.yyyy;
  vec4 h = 1.0 - abs(x) - abs(y);

  vec4 b0 = vec4( x.xy, y.xy );
  vec4 b1 = vec4( x.zw, y.zw );

  vec4 s0 = floor(b0)*2.0 + 1.0;
  vec4 s1 = floor(b1)*2.0 + 1.0;
  vec4 sh = -step(h, vec4(0.0));

  vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy ;
  vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww ;

  vec3 p0 = vec3(a0.xy,h.x);
  vec3 p1 = vec3(a0.zw,h.y);
  vec3 p2 = vec3(a1.xy,h.z);
  vec3 p3 = vec3(a1.zw,h.w);

  vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2, p2), dot(p3,p3)));
  p0 *= norm.x;
  p1 *= norm.y;
  p2 *= norm.z;
  p3 *= norm.w;

  vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
  m = m * m;
  return 42.0 * dot( m*m, vec4( dot(p0,x0), dot(p1,x1),
                                dot(p2,x2), dot(p3,x3) ) );
}
`;

const driftVertex = `
uniform float uTime;
uniform float uTurbulence;
uniform vec3 uWindDirection;
uniform float uSize;

attribute vec3 aInitialPosition;
attribute vec3 aVelocity;
attribute float aPhase;
attribute float aIsBillboard;

#ifndef USE_INSTANCING_COLOR
  attribute vec3 instanceColor;
#endif

varying vec3 vColor;
varying float vIsBillboard;
varying vec2 vUv;

${simplexNoiseGLSL}

void main() {
  vColor = instanceColor;
  vIsBillboard = aIsBillboard;
  vUv = uv;
  
  // Calculate animation offset (excluding aInitialPosition since it is in instanceMatrix)
  vec3 offset = aVelocity * uTime;
  
  // Add Simplex turbulence
  vec3 noisePos = (aInitialPosition + offset) * 0.05 + vec3(aPhase);
  vec3 turbulence = vec3(
    snoise(noisePos),
    snoise(noisePos + vec3(100.0)),
    snoise(noisePos + vec3(200.0))
  ) * uTurbulence;
  
  offset += turbulence;
  
  // Apply wind vector
  offset += uWindDirection * uTime * 0.1;
  
  #ifdef USE_INSTANCING
    vec4 mvPosition = modelViewMatrix * instanceMatrix * vec4(position + offset, 1.0);
  #else
    vec4 mvPosition = modelViewMatrix * vec4(position + aInitialPosition + offset, 1.0);
  #endif
  
  gl_Position = projectionMatrix * mvPosition;
  
  // Size attenuation by distance
  gl_PointSize = uSize * (300.0 / -mvPosition.z);
}
`;

const orbitVertex = `
uniform float uTime;
uniform vec3 uCenter;
uniform float uRadius;
uniform float uSpeed;
uniform float uSize;

attribute vec3 aInitialPosition;
attribute float aOrbitPhase;
attribute float aIsBillboard;

#ifndef USE_INSTANCING_COLOR
  attribute vec3 instanceColor;
#endif

varying vec3 vColor;
varying float vIsBillboard;
varying vec2 vUv;

void main() {
  vColor = instanceColor;
  vIsBillboard = aIsBillboard;
  vUv = uv;
  
  // Compute circular orbit around center
  float angle = aOrbitPhase + uTime * uSpeed;
  vec3 orbitPos = uCenter + vec3(
    cos(angle) * uRadius,
    sin(angle) * uRadius * 0.5,
    sin(angle * 2.0) * uRadius * 0.3
  );
  
  // Linear blend from initial coordinates to the orbit path over time
  float blend = min(1.0, uTime * 0.5);
  vec3 targetPos = mix(aInitialPosition, orbitPos, blend);
  
  // Offset relative to aInitialPosition (since instanceMatrix translates by aInitialPosition)
  vec3 offset = targetPos - aInitialPosition;
  
  #ifdef USE_INSTANCING
    vec4 mvPosition = modelViewMatrix * instanceMatrix * vec4(position + offset, 1.0);
  #else
    vec4 mvPosition = modelViewMatrix * vec4(position + aInitialPosition + offset, 1.0);
  #endif
  
  gl_Position = projectionMatrix * mvPosition;
  gl_PointSize = uSize * (300.0 / -mvPosition.z);
}
`;

const explosionVertex = `
uniform float uTime;
uniform vec3 uOrigin;
uniform float uForce;
uniform vec3 uGravity;
uniform float uDamping;
uniform float uSize;

attribute vec3 aInitialPosition;
attribute vec3 aDirection;
attribute float aSpeed;
attribute float aIsBillboard;

#ifndef USE_INSTANCING_COLOR
  attribute vec3 instanceColor;
#endif

varying vec3 vColor;
varying float vIsBillboard;
varying vec2 vUv;

void main() {
  vColor = instanceColor;
  vIsBillboard = aIsBillboard;
  vUv = uv;
  float t = uTime;
  
  // Physics formula: position = origin + velocity * t + 0.5 * gravity * t^2
  vec3 velocity = aDirection * aSpeed * uForce;
  
  // Apply exponential damping drag force
  vec3 dampedVelocity = velocity * exp(-uDamping * t);
  
  // Add a small constant drift component that persists after the explosion dampens
  vec3 drift = aDirection * aSpeed * 0.08;
  vec3 explosionPos = uOrigin + (dampedVelocity + drift) * t + 0.5 * uGravity * t * t;
  
  // Offset relative to aInitialPosition (since instanceMatrix translates by aInitialPosition)
  vec3 offset = explosionPos - aInitialPosition;
  
  #ifdef USE_INSTANCING
    vec4 mvPosition = modelViewMatrix * instanceMatrix * vec4(position + offset, 1.0);
  #else
    vec4 mvPosition = modelViewMatrix * vec4(position + aInitialPosition + offset, 1.0);
  #endif
  
  gl_Position = projectionMatrix * mvPosition;
  gl_PointSize = uSize * (300.0 / -mvPosition.z);
}
`;

const clusterVertex = `
uniform float uTime;
uniform vec3 uClusterCenters[10];
uniform float uAttractionStrength;
uniform float uSize;

attribute vec3 aInitialPosition;
attribute float aClusterIndex;
attribute float aIsBillboard;

#ifndef USE_INSTANCING_COLOR
  attribute vec3 instanceColor;
#endif

varying vec3 vColor;
varying float vIsBillboard;
varying vec2 vUv;

void main() {
  vColor = instanceColor;
  vIsBillboard = aIsBillboard;
  vUv = uv;
  
  // Select cluster target center dynamically using simple comparisons (100% GLSL ES 1.00 compliant)
  vec3 target = uClusterCenters[0];
  float idx = clamp(aClusterIndex, 0.0, 9.0);
  if (idx < 1.5) {
    target = uClusterCenters[0];
  } else if (idx < 2.5) {
    target = uClusterCenters[1];
  } else if (idx < 3.5) {
    target = uClusterCenters[2];
  } else if (idx < 4.5) {
    target = uClusterCenters[3];
  } else if (idx < 5.5) {
    target = uClusterCenters[4];
  } else if (idx < 6.5) {
    target = uClusterCenters[5];
  } else if (idx < 7.5) {
    target = uClusterCenters[6];
  } else if (idx < 8.5) {
    target = uClusterCenters[7];
  } else if (idx < 9.5) {
    target = uClusterCenters[8];
  } else {
    target = uClusterCenters[9];
  }
  
  // Exponential interpolation towards target coordinates
  float factor = 1.0 - exp(-uTime * uAttractionStrength);
  vec3 targetPos = mix(aInitialPosition, target, factor);
  
  vec3 offset = targetPos - aInitialPosition;
  
  #ifdef USE_INSTANCING
    vec4 mvPosition = modelViewMatrix * instanceMatrix * vec4(position + offset, 1.0);
  #else
    vec4 mvPosition = modelViewMatrix * vec4(position + aInitialPosition + offset, 1.0);
  #endif
  
  gl_Position = projectionMatrix * mvPosition;
  gl_PointSize = uSize * (300.0 / -mvPosition.z);
}
`;

const networkVertex = `
uniform float uTime;
uniform float uFlowSpeed;
uniform float uSize;

attribute vec3 aStartPos;
attribute vec3 aEndPos;
attribute float aFlowOffset;
attribute float aIsBillboard;

#ifndef USE_INSTANCING_COLOR
  attribute vec3 instanceColor;
#endif

varying vec3 vColor;
varying float vIsBillboard;
varying vec2 vUv;

void main() {
  vColor = instanceColor;
  vIsBillboard = aIsBillboard;
  vUv = uv;
  
  // Fractional loop along the connection length
  float flowT = fract(uTime * uFlowSpeed + aFlowOffset);
  vec3 flowPos = mix(aStartPos, aEndPos, flowT);
  
  // Since instanceMatrix translates by aInitialPosition (which is aStartPos)
  vec3 offset = flowPos - aStartPos;
  
  // Pulse size intensity (maximum at midpoint)
  float intensity = sin(flowT * 3.1415926);
  
  #ifdef USE_INSTANCING
    vec4 mvPosition = modelViewMatrix * instanceMatrix * vec4(position + offset, 1.0);
  #else
    vec4 mvPosition = modelViewMatrix * vec4(position + aStartPos + offset, 1.0);
  #endif
  
  gl_Position = projectionMatrix * mvPosition;
  gl_PointSize = uSize * intensity * (300.0 / -mvPosition.z);
}
`;

const particleFragment = `
varying vec3 vColor;
varying float vIsBillboard;
varying vec2 vUv;

void main() {
  float alpha = 1.0;
  
  if (vIsBillboard > 0.5) {
    // Discard fragments outside the unit circle to render a circular particle
    vec2 center = vUv - vec2(0.5);
    float dist = length(center);
    if (dist > 0.5) discard;
    
    // Sharp, anti-aliased edge to prevent blurry halo effects and keep particles precise
    alpha = 1.0 - smoothstep(0.45, 0.48, dist);
  }
  
  gl_FragColor = vec4(vColor, alpha);
}
`;

const hashNoiseGLSL = `
// Fast, lightweight 3D hash-based pseudo-random noise for gas turbulence
float hash3(vec3 p) {
  p = fract(p * 0.3183099 + 0.1);
  p *= 17.0;
  return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
}

float noise3(vec3 p) {
  vec3 i = floor(p);
  vec3 f = fract(p);
  vec3 u = f * f * (3.0 - 2.0 * f);
  
  return mix(
    mix(mix(hash3(i + vec3(0.0,0.0,0.0)), hash3(i + vec3(1.0,0.0,0.0)), u.x),
        mix(hash3(i + vec3(0.0,1.0,0.0)), hash3(i + vec3(1.0,1.0,0.0)), u.x), u.y),
    mix(mix(hash3(i + vec3(0.0,0.0,1.0)), hash3(i + vec3(1.0,0.0,1.0)), u.x),
        mix(hash3(i + vec3(0.0,1.0,1.0)), hash3(i + vec3(1.0,1.0,1.0)), u.x), u.y), u.z
  );
}
`;

const nebulaVertex = `
uniform float uTime;
uniform float uTurbulence;
uniform vec3 uWindDirection;

attribute vec3 aInitialPosition;
attribute vec3 aVelocity;
attribute float aPhase;
attribute float aIsBillboard;
attribute float aCloudType; // 0.0=Background, 1.0=Mid, 2.0=Stars
attribute float aCustomSize;

#ifndef USE_INSTANCING_COLOR
  attribute vec3 instanceColor;
#endif

varying vec3 vColor;
varying float vIsBillboard;
varying vec2 vUv;
varying float vPhase;
varying float vCloudType;

${hashNoiseGLSL}

void main() {
  vColor = instanceColor;
  vIsBillboard = aIsBillboard;
  vUv = uv;
  vPhase = aPhase;
  vCloudType = aCloudType;
  
  vec3 offset = aVelocity * uTime;
  
  // High-frequency turbulence for gas drifting
  vec3 noisePos = (aInitialPosition + offset) * 0.02 + vec3(aPhase);
  vec3 turbulence = vec3(
    noise3(noisePos),
    noise3(noisePos + vec3(80.0)),
    noise3(noisePos + vec3(160.0))
  ) * uTurbulence;
  
  offset += turbulence;
  offset += uWindDirection * uTime * 0.05;
  
  vec3 localPos = position * aCustomSize;
  vec3 worldPos = aInitialPosition + offset;
  
  // Apply rotation around Z-axis based on cloud type (creates orbital parallax)
  float angle = uTime * (aCloudType < 0.5 ? 0.015 : (aCloudType < 1.5 ? 0.025 : 0.008));
  float cosA = cos(angle);
  float sinA = sin(angle);
  
  vec3 rotatedCenter = vec3(
    worldPos.x * cosA - worldPos.y * sinA,
    worldPos.x * sinA + worldPos.y * cosA,
    worldPos.z
  );
  
  vec4 mvPosition = modelViewMatrix * vec4(rotatedCenter + localPos, 1.0);
  
  gl_Position = projectionMatrix * mvPosition;
  
  // Point size attenuation
  gl_PointSize = aCustomSize * (350.0 / -mvPosition.z);
}
`;

const nebulaFragment = `
uniform float uTime;
varying vec3 vColor;
varying float vIsBillboard;
varying vec2 vUv;
varying float vPhase;
varying float vCloudType;

void main() {
  vec2 center = vUv - vec2(0.5);
  float dist = length(center);
  if (dist > 0.5) discard;
  
  float alpha = 1.0;
  
  // Type-based falloffs and opacities
  if (vCloudType < 0.5) {
    // 1. Large background nebula: soft, wide falloff (darker, faster decay)
    alpha = pow(max(0.0, 1.0 - dist * 2.0), 1.8) * 0.08;
  } else if (vCloudType < 1.5) {
    // 2. Medium nebula: moderate density (tighter boundaries)
    alpha = pow(max(0.0, 1.0 - dist * 2.0), 2.5) * 0.15;
  } else {
    // 3. Small stars: tight, sharp center + independent twinkling (perfectly pin-sharp)
    float twinkle = 0.5 + 0.5 * sin(uTime * 3.0 + vPhase);
    alpha = pow(max(0.0, 1.0 - dist * 2.0), 6.0) * 0.95 * twinkle;
  }
  
  // Color shifting: add orange/magenta gas variance
  vec3 finalColor = vColor;
  if (vCloudType < 1.5) {
    if (vPhase > 120.0) {
      finalColor = mix(vColor, vec3(0.925, 0.282, 0.600), 0.35); // Purple -> Pink
    } else if (vPhase > 40.0) {
      finalColor = mix(vColor, vec3(0.976, 0.450, 0.098), 0.40); // Pink -> Orange
    }
  } else {
    // Stars color shifting: white/blue twinkling
    if (vPhase > 100.0) {
      finalColor = mix(vColor, vec3(0.376, 0.647, 0.980), 0.30); // White -> Blue-white
    }
  }
  
  gl_FragColor = vec4(finalColor, alpha);
}
`;

export const particleShaders = {
  drift: { vertex: driftVertex, fragment: particleFragment },
  orbit: { vertex: orbitVertex, fragment: particleFragment },
  explosion: { vertex: explosionVertex, fragment: particleFragment },
  cluster: { vertex: clusterVertex, fragment: particleFragment },
  network: { vertex: networkVertex, fragment: particleFragment },
  nebula: { vertex: nebulaVertex, fragment: nebulaFragment },
};

