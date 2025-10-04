class LiquidEther {
  constructor(selector, options = {}) {
    this.container = document.querySelector(selector);
    if (!this.container) return;

    // Default options
    this.options = Object.assign({
      colors: ['#5227FF', '#FF9FFC', '#B19EEF'],
      background: 'transparent',
      speed: 0.5,
      spread: 0.5,
      size: 100,
      mouseForce: 20,
      autoDemo: true,
    }, options);

    this.init();
  }

  init() {
    const width = this.container.offsetWidth;
    const height = this.container.offsetHeight;

    // Three.js setup
    this.scene = new THREE.Scene();
    this.camera = new THREE.Camera();
    this.renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(window.devicePixelRatio || 1);
    this.container.appendChild(this.renderer.domElement);

    this.clock = new THREE.Clock();

    this.createParticles();
    this.addEvents();
    this.animate();
  }

  createParticles() {
    const geometry = new THREE.BufferGeometry();
    const count = 300; // number of particles
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);

    const color = new THREE.Color();
    for (let i = 0; i < count; i++) {
      positions[i * 3 + 0] = (Math.random() * 2 - 1);
      positions[i * 3 + 1] = (Math.random() * 2 - 1);
      positions[i * 3 + 2] = 0;

      color.set(this.options.colors[Math.floor(Math.random() * this.options.colors.length)]);
      colors[i * 3 + 0] = color.r;
      colors[i * 3 + 1] = color.g;
      colors[i * 3 + 2] = color.b;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
      size: this.options.size,
      vertexColors: true,
      transparent: true,
      opacity: 0.8,
    });

    this.particles = new THREE.Points(geometry, material);
    this.scene.add(this.particles);
  }

  addEvents() {
    this.mouse = new THREE.Vector2();
    this.container.addEventListener('mousemove', e => {
      const rect = this.container.getBoundingClientRect();
      this.mouse.x = (e.clientX - rect.left) / rect.width * 2 - 1;
      this.mouse.y = -(e.clientY - rect.top) / rect.height * 2 + 1;
    });
    window.addEventListener('resize', () => this.onResize());
  }

  onResize() {
    const width = this.container.offsetWidth;
    const height = this.container.offsetHeight;
    this.renderer.setSize(width, height);
  }

  animate() {
    this.updateParticles();
    this.renderer.render(this.scene, this.camera);
    requestAnimationFrame(() => this.animate());
  }

  updateParticles() {
    const positions = this.particles.geometry.attributes.position.array;
    for (let i = 0; i < positions.length; i += 3) {
      positions[i] += (Math.random() - 0.5) * 0.01 * this.options.speed;
      positions[i + 1] += (Math.random() - 0.5) * 0.01 * this.options.speed;

      // Simple mouse interaction
      const dx = this.mouse.x - positions[i];
      const dy = this.mouse.y - positions[i + 1];
      positions[i] += dx * 0.01 * this.options.spread;
      positions[i + 1] += dy * 0.01 * this.options.spread;
    }
    this.particles.geometry.attributes.position.needsUpdate = true;
  }
}
