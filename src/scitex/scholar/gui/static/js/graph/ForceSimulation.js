/**
 * ForceSimulation - Force-directed graph physics engine
 *
 * Repulsion, attraction, centering, velocity damping.
 * Ported from scitex-cloud (standalone, no ES6 modules).
 */
class ForceSimulation {
  constructor(nodes, edges, width, height) {
    this.nodes = nodes;
    this.edges = edges;
    this.width = width;
    this.height = height;
    this.alpha = 1;
    this.alphaDecay = 0.02;
    this.alphaMin = 0.001;
    this.tickCallback = null;
    this.animationId = null;
  }

  onTick(callback) {
    this.tickCallback = callback;
  }

  start() {
    this.alpha = 1;
    this.tick();
  }

  stop() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
  }

  reheat() {
    this.alpha = Math.max(this.alpha, 0.3);
    if (!this.animationId) this.tick();
  }

  tick() {
    if (this.alpha < this.alphaMin) {
      this.animationId = null;
      return;
    }
    this.applyForces();
    this.alpha *= 1 - this.alphaDecay;
    if (this.tickCallback) this.tickCallback();
    this.animationId = requestAnimationFrame(() => this.tick());
  }

  applyForces() {
    const centerX = this.width / 2;
    const centerY = this.height / 2;

    this.nodes.forEach((node) => {
      if (node.fx != null) node.x = node.fx;
      if (node.fy != null) node.y = node.fy;
    });

    this.applyRepulsion();
    this.applyAttraction();
    this.applyCentering(centerX, centerY);
    this.applyVelocities();
  }

  applyRepulsion() {
    for (let i = 0; i < this.nodes.length; i++) {
      for (let j = i + 1; j < this.nodes.length; j++) {
        const a = this.nodes[i];
        const b = this.nodes[j];
        const dx = (b.x || 0) - (a.x || 0);
        const dy = (b.y || 0) - (a.y || 0);
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const force = (500 / (dist * dist)) * this.alpha;
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;

        if (a.fx == null) {
          a.vx = (a.vx || 0) - fx;
          a.vy = (a.vy || 0) - fy;
        }
        if (b.fx == null) {
          b.vx = (b.vx || 0) + fx;
          b.vy = (b.vy || 0) + fy;
        }
      }
    }
  }

  applyAttraction() {
    this.edges.forEach((edge) => {
      const source = edge.source;
      const target = edge.target;
      const dx = (target.x || 0) - (source.x || 0);
      const dy = (target.y || 0) - (source.y || 0);
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      const force = (dist - 100) * 0.05 * this.alpha;
      const fx = (dx / dist) * force;
      const fy = (dy / dist) * force;

      if (source.fx == null) {
        source.vx = (source.vx || 0) + fx;
        source.vy = (source.vy || 0) + fy;
      }
      if (target.fx == null) {
        target.vx = (target.vx || 0) - fx;
        target.vy = (target.vy || 0) - fy;
      }
    });
  }

  applyCentering(centerX, centerY) {
    this.nodes.forEach((node) => {
      if (node.fx == null) {
        node.vx =
          (node.vx || 0) + (centerX - (node.x || 0)) * 0.01 * this.alpha;
        node.vy =
          (node.vy || 0) + (centerY - (node.y || 0)) * 0.01 * this.alpha;
      }
    });
  }

  applyVelocities() {
    const padding = 50;
    this.nodes.forEach((node) => {
      if (node.fx == null) {
        node.vx = (node.vx || 0) * 0.6;
        node.vy = (node.vy || 0) * 0.6;
        node.x = (node.x || 0) + (node.vx || 0);
        node.y = (node.y || 0) + (node.vy || 0);
        node.x = Math.max(padding, Math.min(this.width - padding, node.x));
        node.y = Math.max(padding, Math.min(this.height - padding, node.y));
      }
    });
  }
}
