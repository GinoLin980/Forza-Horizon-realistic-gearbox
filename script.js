document.addEventListener('DOMContentLoaded', function() {
  var controller = new ScrollMagic.Controller();
  var deviceHeight = window.innerHeight;

  function isMobile() {
      return /android|bb\d+|meego.+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(navigator.userAgent || navigator.vendor || window.opera);
  }

  if (isMobile()) {
      document.body.classList.add('mobile');
      document.getElementById('features').style.height = '80vh';
      document.querySelector('#setup-instructions').style.height = 'auto';
      document.querySelector('#main').style.height = '80vh';
  }

  // Create a GSAP timeline for feature items
  var featureTimeline = gsap.timeline({paused: true});

  document.querySelectorAll('.feature-item').forEach((item, index) => {
      featureTimeline.fromTo(item,
          { scale: 3.5, opacity: 0 },
          { scale: 1, opacity: 1, duration: 0.5, delay: index * 0.2 },
          index * 0.3
      );
  });

  // Create the feature scene
  var featureScene = new ScrollMagic.Scene({
      triggerElement: "#features",
      triggerHook: isMobile() ? 0 : 0,
      duration: isMobile() ? '200%' : deviceHeight,
      offset: isMobile() ? 50 : 0
  })
  .setPin("#features", {pushFollowers: true})
  .on("enter", function() {
      featureTimeline.play();
  })
  .addTo(controller);

  // Canvas setup and animation code remains unchanged
  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');

  function resizeCanvas() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
  }

  resizeCanvas();

  let curves = [];
  let bubbles = [];

  class Curve {
      constructor() {
          this.startX = Math.random() * canvas.width;
          this.startY = Math.random() * canvas.height;
          this.controlX = Math.random() * canvas.width;
          this.controlY = Math.random() * canvas.height;
          this.endX = Math.random() * canvas.width;
          this.endY = Math.random() * canvas.height;
          this.speed = Math.random() * 0.5 + 0.1;
          this.startColor = this.getRandomColor();
          this.endColor = this.getRandomColor();
      }

      getRandomColor() {
          const r = Math.floor(Math.random() * 100) + 100;
          const g = Math.floor(Math.random() * 100);
          const b = Math.floor(Math.random() * 155) + 100;
          return `rgb(${r},${g},${b})`;
      }

      update() {
          this.startY += this.speed;
          this.controlY += this.speed;
          this.endY += this.speed;
          if (this.startY > canvas.height) {
              this.startY = -100;
              this.controlY = -50;
              this.endY = 0;
              this.startX = Math.random() * canvas.width;
              this.controlX = Math.random() * canvas.width;
              this.endX = Math.random() * canvas.width;
              this.startColor = this.getRandomColor();
              this.endColor = this.getRandomColor();
          }
      }

      draw() {
          const gradient = ctx.createLinearGradient(this.startX, this.startY, this.endX, this.endY);
          gradient.addColorStop(0, this.startColor);
          gradient.addColorStop(1, this.endColor);
          ctx.beginPath();
          ctx.moveTo(this.startX, this.startY);
          ctx.quadraticCurveTo(this.controlX, this.controlY, this.endX, this.endY);
          ctx.strokeStyle = gradient;
          ctx.lineWidth = 3;
          ctx.stroke();
      }
  }

  class Bubble {
      constructor() {
          this.x = Math.random() * canvas.width;
          this.y = canvas.height + Math.random() * 100;
          this.radius = Math.random() * 5 + 2;
          this.speed = Math.random() * 1 + 0.5;
      }

      update() {
          this.y -= this.speed;
          if (this.y + this.radius < 0) {
              this.y = canvas.height + this.radius;
          }
      }

      draw() {
          ctx.beginPath();
          ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
          ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
          ctx.fill();
      }
  }

  function init() {
      curves = [];
      bubbles = [];
      for (let i = 0; i < (isMobile() ? 7 : 10); i++) {
          curves.push(new Curve());
      }
      for (let i = 0; i < (isMobile() ? 15 : 20); i++) {
          bubbles.push(new Bubble());
      }
  }

  function animate() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      curves.forEach(curve => {
          curve.update();
          curve.draw();
      });
      bubbles.forEach(bubble => {
          bubble.update();
          bubble.draw();
      });
      requestAnimationFrame(animate);
  }

  init();
  animate();
  window.addEventListener('resize', () => {
    resizeCanvas();
});
})