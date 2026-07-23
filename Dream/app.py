import json
import random
import re

import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(
    page_title="WHERE HAVE YOU BEEN?",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 20% 20%, rgba(255,220,238,.65), transparent 34%),
            radial-gradient(circle at 80% 15%, rgba(199,231,255,.55), transparent 32%),
            linear-gradient(160deg, #f6ddec 0%, #dce9ff 48%, #ded3f5 100%);
    }
    h1, h2, h3, p, label { color: #4f4962 !important; }
    .block-container { max-width: 1280px; padding-top: 2rem; }
    div[data-testid="stTextArea"] textarea {
        background: rgba(255,255,255,.58);
        border: 1px solid rgba(255,255,255,.85);
        border-radius: 18px;
        color: #4f4962;
    }
    div.stButton > button {
        width: 100%;
        border: 1px solid rgba(255,255,255,.9);
        border-radius: 999px;
        background: rgba(255,255,255,.56);
        color: #5a526d;
        font-weight: 700;
    }
    div.stButton > button:hover {
        border-color: #fff;
        background: rgba(255,255,255,.78);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

PALETTES = {
    "Cotton Candy": {
        "sky": "#f7c9df", "fog": "#d8dcf5", "ground": "#d7f0e8",
        "accent": "#fff2a8", "object": "#cdb7e9"
    },
    "Pool Memory": {
        "sky": "#bee7f4", "fog": "#dceefa", "ground": "#d7f6f1",
        "accent": "#f8cfe0", "object": "#b4c9ed"
    },
    "Lavender Evening": {
        "sky": "#bfb3e6", "fog": "#d8cced", "ground": "#cabfe0",
        "accent": "#ffd6e8", "object": "#8da6cf"
    },
    "Yellow Playground": {
        "sky": "#cbe8ff", "fog": "#f1e6d2", "ground": "#e8e2ad",
        "accent": "#f8bcd6", "object": "#a9c6e8"
    },
}

def analyse_prompt(prompt: str, palette_name: str, fog: int, weirdness: int, seed: int) -> dict:
    """Rule-based prompt parser for the first prototype."""
    text = prompt.lower()

    scene = "field"
    keyword_groups = {
        "pool": ["수영장", "수영", "물속", "pool", "water"],
        "school": ["학교", "교실", "복도", "school", "classroom", "hallway"],
        "playground": ["놀이터", "미끄럼틀", "그네", "playground", "slide", "swing"],
        "room": ["방", "침실", "거실", "room", "bedroom", "house"],
        "field": ["들판", "잔디", "초원", "field", "grass", "meadow"],
    }
    for key, words in keyword_groups.items():
        if any(word in text for word in words):
            scene = key
            break

    palette = PALETTES[palette_name].copy()
    rng = random.Random(seed)

    objects = []
    object_keywords = {
        "moon": ["달", "moon"],
        "door": ["문", "door"],
        "telephone": ["전화", "전화기", "phone", "telephone"],
        "chair": ["의자", "chair"],
        "cloud": ["구름", "cloud"],
        "tree": ["나무", "tree"],
        "eye": ["눈", "eye"],
        "tv": ["텔레비전", "티비", "tv", "television"],
    }
    for obj, words in object_keywords.items():
        if any(word in text for word in words):
            objects.append(obj)

    defaults = {
        "pool": ["door", "telephone", "cloud"],
        "school": ["door", "chair", "clock"],
        "playground": ["cloud", "moon", "tree"],
        "room": ["tv", "door", "telephone"],
        "field": ["cloud", "moon", "door"],
    }
    for obj in defaults[scene]:
        if obj not in objects:
            objects.append(obj)

    messages = [
        "YOU HAVE BEEN HERE BEFORE",
        "DON'T WAKE UP YET",
        "WHERE HAVE YOU BEEN?",
        "THIS PLACE REMEMBERS YOU",
        "여기는 네가 입력하지 않았다",
    ]

    return {
        "prompt": prompt,
        "scene": scene,
        "palette": palette,
        "fogDensity": round(0.008 + fog * 0.00055, 4),
        "weirdness": weirdness,
        "seed": seed,
        "objects": objects[:6],
        "message": rng.choice(messages),
    }

st.title("WHERE HAVE YOU BEEN?")
st.caption("Describe a place. Then enter it.")

with st.form("world_form"):
    prompt = st.text_area(
        "어디에 있었나요?",
        value="구름 위에 있는 텅 빈 수영장. 물속에는 분홍색 문이 있고, 멀리서 전화벨이 들린다.",
        height=120,
    )
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        palette_name = st.selectbox("색채", list(PALETTES.keys()))
    with col2:
        fog = st.slider("안개", 0, 100, 55)
    with col3:
        weirdness = st.slider("기괴함", 0, 100, 62)
    with col4:
        seed = st.number_input("세계 번호", 1, 9999, 404)
    submitted = st.form_submit_button("ENTER THE DREAM")

if submitted or "world_config" not in st.session_state:
    st.session_state.world_config = analyse_prompt(
        prompt, palette_name, fog, weirdness, int(seed)
    )

config_json = json.dumps(st.session_state.world_config, ensure_ascii=False)

WORLD_HTML = r"""
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<style>
  html, body { margin:0; width:100%; height:100%; overflow:hidden; background:#111; }
  #world { position:relative; width:100%; height:760px; overflow:hidden; border-radius:22px; }
  canvas { display:block; }
  #overlay {
    position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
    background:linear-gradient(180deg,rgba(255,255,255,.12),rgba(55,45,75,.25));
    color:white; font-family:Georgia,serif; text-align:center; z-index:5;
    backdrop-filter:blur(3px);
  }
  #panel {
    width:min(520px,82%); padding:30px; border:1px solid rgba(255,255,255,.58);
    border-radius:24px; background:rgba(255,255,255,.15);
    box-shadow:0 18px 80px rgba(60,40,85,.22);
  }
  #panel h2 { letter-spacing:.14em; font-size:24px; margin:0 0 12px; }
  #panel p { line-height:1.7; opacity:.92; }
  #enter {
    border:1px solid white; border-radius:999px; padding:12px 25px;
    background:rgba(255,255,255,.25); color:white; cursor:pointer;
    font-weight:bold; letter-spacing:.08em;
  }
  #hud {
    position:absolute; left:18px; bottom:16px; z-index:4; color:white;
    font:13px/1.5 Arial,sans-serif; text-shadow:0 1px 8px rgba(0,0,0,.4);
    opacity:.88; pointer-events:none;
  }
  #message {
    position:absolute; left:50%; top:14%; transform:translateX(-50%);
    color:white; font:600 19px Georgia,serif; letter-spacing:.12em;
    text-shadow:0 2px 12px rgba(65,50,90,.65); z-index:3;
    opacity:0; transition:opacity 1.3s; white-space:nowrap; pointer-events:none;
  }
  #crosshair {
    position:absolute; left:50%; top:50%; width:5px; height:5px;
    transform:translate(-50%,-50%); border:1px solid rgba(255,255,255,.75);
    border-radius:50%; z-index:3; pointer-events:none;
  }
</style>
</head>
<body>
<div id="world">
  <div id="overlay">
    <div id="panel">
      <h2>WHERE HAVE YOU BEEN?</h2>
      <p id="promptText"></p>
      <button id="enter">CLICK TO ENTER</button>
      <p style="font-size:12px">WASD 이동 · 마우스 시점 · ESC 나가기 · 음악은 입장 후 시작됩니다</p>
    </div>
  </div>
  <div id="message"></div>
  <div id="crosshair"></div>
  <div id="hud">WASD TO MOVE<br>ESC TO WAKE UP</div>
</div>

<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/"
  }
}
</script>
<script type="module">
import * as THREE from 'three';
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';

const CONFIG = __CONFIG__;
const container = document.getElementById('world');
const overlay = document.getElementById('overlay');
const enter = document.getElementById('enter');
const message = document.getElementById('message');
document.getElementById('promptText').textContent = CONFIG.prompt;

const scene = new THREE.Scene();
scene.background = new THREE.Color(CONFIG.palette.sky);
scene.fog = new THREE.FogExp2(CONFIG.palette.fog, CONFIG.fogDensity);

const camera = new THREE.PerspectiveCamera(72, container.clientWidth / container.clientHeight, 0.1, 700);
camera.position.set(0, 1.7, 8);

const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(container.clientWidth, container.clientHeight);
renderer.shadowMap.enabled = true;
renderer.outputColorSpace = THREE.SRGBColorSpace;
container.prepend(renderer.domElement);

const controls = new PointerLockControls(camera, renderer.domElement);
enter.addEventListener('click', () => {
  controls.lock();
  startAudio();
});
controls.addEventListener('lock', () => overlay.style.display = 'none');
controls.addEventListener('unlock', () => overlay.style.display = 'flex');

scene.add(new THREE.HemisphereLight(0xffffff, 0x8f82a8, 2.6));
const sun = new THREE.DirectionalLight(0xfff4df, 2.0);
sun.position.set(20, 35, 10);
sun.castShadow = true;
scene.add(sun);

const mat = (color, roughness=.8, emissive=0x000000) =>
  new THREE.MeshStandardMaterial({color, roughness, metalness:.03, emissive});

function box(w,h,d,color,x,y,z) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w,h,d), mat(color));
  m.position.set(x,y,z); m.castShadow = true; m.receiveShadow = true; scene.add(m); return m;
}
function sphere(r,color,x,y,z) {
  const m = new THREE.Mesh(new THREE.SphereGeometry(r,24,16), mat(color));
  m.position.set(x,y,z); m.castShadow = true; scene.add(m); return m;
}
function cylinder(r1,r2,h,color,x,y,z) {
  const m = new THREE.Mesh(new THREE.CylinderGeometry(r1,r2,h,18), mat(color));
  m.position.set(x,y,z); m.castShadow = true; scene.add(m); return m;
}

const ground = new THREE.Mesh(
  new THREE.PlaneGeometry(500,500),
  mat(CONFIG.palette.ground)
);
ground.rotation.x = -Math.PI/2;
ground.receiveShadow = true;
scene.add(ground);

function createCloud(x,y,z,s=1) {
  const group = new THREE.Group();
  [[0,0,0,1.2],[1,0.1,0,.9],[-1,.05,0,.8],[.3,.35,0,.75]].forEach(v=>{
    const c = new THREE.Mesh(new THREE.SphereGeometry(v[3]*s,18,12), mat(0xffffff));
    c.position.set(v[0]*s,v[1]*s,v[2]); group.add(c);
  });
  group.position.set(x,y,z); scene.add(group);
}
function createDoor(x,z,rotation=0) {
  const g = new THREE.Group();
  const frame = box(2.5,3.8,.24,CONFIG.palette.object,0,0,0);
  scene.remove(frame); g.add(frame);
  const inner = new THREE.Mesh(new THREE.BoxGeometry(1.85,3.3,.18), mat(CONFIG.palette.accent));
  inner.position.z=.18; g.add(inner);
  const knob = new THREE.Mesh(new THREE.SphereGeometry(.08,12,8), mat(0xffffff));
  knob.position.set(.68,0,.32); g.add(knob);
  g.position.set(x,1.9,z); g.rotation.y=rotation; scene.add(g);
}
function createTelephone(x,z) {
  const g = new THREE.Group();
  const base = new THREE.Mesh(new THREE.BoxGeometry(1.1,.35,.75),mat(CONFIG.palette.accent));
  const handle = new THREE.Mesh(new THREE.BoxGeometry(1.15,.18,.22),mat(CONFIG.palette.object));
  handle.position.y=.32; g.add(base,handle); g.position.set(x,.35,z); scene.add(g);
}
function createPlayground() {
  box(4,.25,1.2,CONFIG.palette.object,-5,.15,-6);
  const slide = box(1.2,.2,5,CONFIG.palette.accent,-5,1.5,-9);
  slide.rotation.x = -.45;
  cylinder(.12,.12,3.5,0xffffff,-6.5,1.75,-8);
  cylinder(.12,.12,3.5,0xffffff,-3.5,1.75,-8);
}
function createPool() {
  box(18,.35,12,0xffffff,0,.12,-8);
  const water = new THREE.Mesh(
    new THREE.PlaneGeometry(15.8,9.8),
    new THREE.MeshStandardMaterial({color:0x9ddde7,transparent:true,opacity:.62,roughness:.18})
  );
  water.rotation.x=-Math.PI/2; water.position.set(0,.34,-8); scene.add(water);
  for(let i=-6;i<=6;i+=2) box(.05,.03,9.4,0xffffff,i,.36,-8);
}
function createSchool() {
  for(let i=0;i<9;i++){
    box(.25,4,7,CONFIG.palette.object,-5,2,-i*7);
    box(.25,4,7,CONFIG.palette.object,5,2,-i*7);
    if(i<8) createDoor(-4.8,-i*7-2,Math.PI/2);
  }
  box(10,.2,65,0xffffff,0,4,-28);
}
function createRoom() {
  box(18,4,.3,CONFIG.palette.object,0,2,-12);
  box(.3,4,20,CONFIG.palette.object,-9,2,-2);
  box(.3,4,20,CONFIG.palette.object,9,2,-2);
  createDoor(0,-11.7,0);
}
function createField() {
  for(let i=0;i<38;i++){
    const x=(Math.random()-.5)*100, z=-Math.random()*110;
    const trunk=cylinder(.18,.24,2.2,0xd9bfaa,x,1.1,z);
    sphere(1.2+(Math.random()*.6),CONFIG.palette.object,x,3,z);
  }
}

if(CONFIG.scene==='pool') createPool();
else if(CONFIG.scene==='school') createSchool();
else if(CONFIG.scene==='playground') createPlayground();
else if(CONFIG.scene==='room') createRoom();
else createField();

for(let i=0;i<18;i++) createCloud((Math.random()-.5)*90,8+Math.random()*16,-20-Math.random()*100,1+Math.random()*2.4);

CONFIG.objects.forEach((obj,i)=>{
  const angle=(i/Math.max(CONFIG.objects.length,1))*Math.PI*2;
  const x=Math.cos(angle)*(7+i*2), z=-14-Math.sin(angle)*(8+i*2);
  if(obj==='door') createDoor(x,z,angle+.5);
  if(obj==='telephone') createTelephone(x,z);
  if(obj==='chair') {
    box(1,.16,1,CONFIG.palette.accent,x,.8,z);
    box(1,.16,.15,CONFIG.palette.accent,x,1.5,z-.45);
    cylinder(.06,.06,1.2,CONFIG.palette.object,x-.38,.6,z-.35);
    cylinder(.06,.06,1.2,CONFIG.palette.object,x+.38,.6,z-.35);
  }
  if(obj==='moon') sphere(7,0xfff1bd,18,25,-60);
  if(obj==='tv') {
    box(2.6,1.8,.5,0x746b89,x,1.2,z);
    box(2.1,1.3,.08,0xc9e8ed,x,1.25,z+.3);
  }
  if(obj==='tree') {
    cylinder(.25,.35,3,0xd5b3a2,x,1.5,z); sphere(1.8,CONFIG.palette.object,x,4,z);
  }
  if(obj==='eye') {
    const eye=sphere(1.4,0xffffff,x,3,z);
    sphere(.55,0x8ea8d0,x,3,z+1.22); sphere(.2,0x222333,x,3,z+1.7);
  }
});

if(CONFIG.weirdness > 35) {
  for(let i=0;i<Math.floor(CONFIG.weirdness/13);i++){
    const scale=1.5+Math.random()*5;
    const floating=box(scale,.25,scale,CONFIG.palette.accent,(Math.random()-.5)*60,4+Math.random()*12,-20-Math.random()*70);
    floating.rotation.set(Math.random(),Math.random(),Math.random());
  }
}
if(CONFIG.weirdness > 70) {
  const upside = new THREE.Mesh(new THREE.PlaneGeometry(55,55),mat(CONFIG.palette.ground));
  upside.rotation.x=Math.PI/2; upside.position.set(0,18,-45); scene.add(upside);
}

const keys={};
document.addEventListener('keydown',e=>keys[e.code]=true);
document.addEventListener('keyup',e=>keys[e.code]=false);
const velocity=new THREE.Vector3();
const direction=new THREE.Vector3();
const clock=new THREE.Clock();

let audioStarted=false;
function startAudio(){
  if(audioStarted) return;
  audioStarted=true;
  const AudioCtx=window.AudioContext||window.webkitAudioContext;
  const ctx=new AudioCtx();
  const master=ctx.createGain(); master.gain.value=.045; master.connect(ctx.destination);

  [110,164.81,220].forEach((freq,i)=>{
    const osc=ctx.createOscillator();
    const gain=ctx.createGain();
    const filter=ctx.createBiquadFilter();
    osc.type=i===0?'sine':'triangle'; osc.frequency.value=freq;
    filter.type='lowpass'; filter.frequency.value=420;
    gain.gain.value=i===0?.5:.18;
    osc.connect(filter).connect(gain).connect(master); osc.start();
  });

  const lfo=ctx.createOscillator(); const lfoGain=ctx.createGain();
  lfo.frequency.value=.07; lfoGain.gain.value=.018;
  lfo.connect(lfoGain).connect(master.gain); lfo.start();

  if(CONFIG.objects.includes('telephone')){
    setInterval(()=>{
      const osc=ctx.createOscillator(); const g=ctx.createGain();
      osc.frequency.value=620; g.gain.setValueAtTime(0,ctx.currentTime);
      g.gain.linearRampToValueAtTime(.06,ctx.currentTime+.03);
      g.gain.exponentialRampToValueAtTime(.001,ctx.currentTime+.65);
      osc.connect(g).connect(ctx.destination); osc.start(); osc.stop(ctx.currentTime+.7);
    },9000);
  }
}

let messageShown=false;
function animate(){
  requestAnimationFrame(animate);
  const delta=Math.min(clock.getDelta(),.05);
  if(controls.isLocked){
    velocity.x-=velocity.x*8*delta;
    velocity.z-=velocity.z*8*delta;
    direction.z=Number(keys['KeyW'])-Number(keys['KeyS']);
    direction.x=Number(keys['KeyD'])-Number(keys['KeyA']);
    direction.normalize();
    const speed=8.5;
    if(keys['KeyW']||keys['KeyS']) velocity.z-=direction.z*speed*delta*8;
    if(keys['KeyA']||keys['KeyD']) velocity.x-=direction.x*speed*delta*8;
    controls.moveRight(-velocity.x*delta);
    controls.moveForward(-velocity.z*delta);
    camera.position.y=1.7;

    const traveled=Math.abs(camera.position.x)+Math.abs(camera.position.z-8);
    if(traveled>18 && !messageShown){
      messageShown=true; message.textContent=CONFIG.message; message.style.opacity=1;
      setTimeout(()=>message.style.opacity=0,4500);
    }
  }
  renderer.render(scene,camera);
}
animate();

window.addEventListener('resize',()=>{
  camera.aspect=container.clientWidth/container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth,container.clientHeight);
});
</script>
</body>
</html>
"""

world_html = WORLD_HTML.replace("__CONFIG__", config_json)
html(world_html, height=780, scrolling=False)

with st.expander("현재 생성된 세계 설정 보기"):
    st.json(st.session_state.world_config)

st.caption(
    "v0.1 · Rule-based procedural dream world · Three.js + Streamlit"
)
