import{j as y}from"./jsx-runtime.DXco-PnT.js";import{r as x}from"./index.BCvWX60U.js";globalThis.process??={};globalThis.process.env??={};const D="/assets/c6b425b1-moser-fume-dial-clean.png",I=`#version 300 es
precision highp float;

uniform vec2 u_resolution;
uniform vec2 u_texSize;
uniform float u_time;
uniform float u_scroll;
uniform sampler2D u_tex;
out vec4 fragColor;

float hash(vec2 p) {
  return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

void main() {
  vec2 uv = gl_FragCoord.xy / u_resolution;

  // object-fit: cover mapping (crop overflow, never distort).
  float screenA = u_resolution.x / u_resolution.y;
  float texA = u_texSize.x / u_texSize.y;
  vec2 ratio = vec2(min(screenA / texA, 1.0), min(texA / screenA, 1.0));
  vec2 uvc = vec2(
    uv.x * ratio.x + (1.0 - ratio.x) * 0.5,
    uv.y * ratio.y + (1.0 - ratio.y) * 0.5
  );

  vec3 base = texture(u_tex, uvc).rgb;
  float luma = dot(base, vec3(0.299, 0.587, 0.114));

  // Twinkle only the bright crystalline flecks. Per-region phase keeps
  // neighbouring sparks out of sync so it shimmers instead of pulsing as one.
  float fleck = smoothstep(0.28, 0.62, luma);
  float phase = hash(floor(uvc * u_texSize * 0.18));
  float twinkle = 0.78 + 0.22 * sin(u_time * 1.9 + phase * 6.2831);
  vec3 col = base + base * fleck * (twinkle - 0.78) * 3.2;

  // Soft light band drifting with scroll — gently lifts flecks it passes over.
  float bandPos = 0.30 + u_scroll * 0.55 + 0.04 * sin(u_time * 0.25);
  float band = smoothstep(0.34, 0.0, abs((uv.x * 0.6 + uv.y * 0.4) - bandPos));
  col += base * fleck * band * 0.5;

  fragColor = vec4(col, 1.0);
}
`,M=`#version 300 es
precision highp float;
const vec2 positions[3] = vec2[3](
  vec2(-1.0, -1.0),
  vec2( 3.0, -1.0),
  vec2(-1.0,  3.0)
);
void main() {
  gl_Position = vec4(positions[gl_VertexID], 0.0, 1.0);
}
`;function R(r,a,o){const e=r.createShader(a);return e?(r.shaderSource(e,o),r.compileShader(e),r.getShaderParameter(e,r.COMPILE_STATUS)?e:(console.error(r.getShaderInfoLog(e)),r.deleteShader(e),null)):null}function X({className:r}){const a=x.useRef(null);return x.useEffect(()=>{const o=a.current;if(!o)return;const e=o.getContext("webgl2",{antialias:!1,alpha:!1,powerPreference:"high-performance"});if(!e)return;const l=R(e,e.VERTEX_SHADER,M),u=R(e,e.FRAGMENT_SHADER,I);if(!l||!u)return;const t=e.createProgram();if(!t)return;if(e.attachShader(t,l),e.attachShader(t,u),e.linkProgram(t),!e.getProgramParameter(t,e.LINK_STATUS)){console.error(e.getProgramInfoLog(t));return}e.useProgram(t);const S=e.getUniformLocation(t,"u_resolution"),A=e.getUniformLocation(t,"u_texSize"),w=e.getUniformLocation(t,"u_time"),b=e.getUniformLocation(t,"u_scroll"),P=e.getUniformLocation(t,"u_tex"),f=window.matchMedia("(prefers-reduced-motion: reduce)").matches,g=Math.min(window.devicePixelRatio||1,1.75);let m=0,s=!0,d=!1;const L=performance.now(),U=()=>{const n=Math.floor(o.clientWidth*g),c=Math.floor(o.clientHeight*g);(o.width!==n||o.height!==c)&&(o.width=n,o.height=c,e.viewport(0,0,n,c)),e.uniform2f(S,n,c)};let _=0;const h=()=>{const n=document.documentElement.scrollHeight-window.innerHeight;_=n>0?Math.min(Math.max(window.scrollY/n,0),1):0},E=()=>{U();const n=(performance.now()-L)/1e3;e.uniform1f(w,f?0:n),e.uniform1f(b,_),e.drawArrays(e.TRIANGLES,0,3)},v=()=>{!s||!d||(E(),f||(m=requestAnimationFrame(v)))},p=e.createTexture(),i=new Image;i.crossOrigin="anonymous",i.onload=()=>{e.bindTexture(e.TEXTURE_2D,p),e.pixelStorei(e.UNPACK_FLIP_Y_WEBGL,!0),e.texImage2D(e.TEXTURE_2D,0,e.RGBA,e.RGBA,e.UNSIGNED_BYTE,i),e.texParameteri(e.TEXTURE_2D,e.TEXTURE_MIN_FILTER,e.LINEAR),e.texParameteri(e.TEXTURE_2D,e.TEXTURE_MAG_FILTER,e.LINEAR),e.texParameteri(e.TEXTURE_2D,e.TEXTURE_WRAP_S,e.CLAMP_TO_EDGE),e.texParameteri(e.TEXTURE_2D,e.TEXTURE_WRAP_T,e.CLAMP_TO_EDGE),e.uniform1i(P,0),e.uniform2f(A,i.naturalWidth,i.naturalHeight),d=!0,v()},i.src=D;const T=()=>{document.hidden?(s=!1,cancelAnimationFrame(m)):f||(s=!0,v())};return window.addEventListener("scroll",h,{passive:!0}),window.addEventListener("resize",()=>{d&&E()}),document.addEventListener("visibilitychange",T),h(),()=>{s=!1,cancelAnimationFrame(m),window.removeEventListener("scroll",h),document.removeEventListener("visibilitychange",T),e.deleteTexture(p),e.deleteProgram(t),e.deleteShader(l),e.deleteShader(u)}},[]),y.jsx("canvas",{ref:a,"aria-hidden":"true",className:r})}export{X as DialCanvas};
