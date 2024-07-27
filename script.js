// GSAP transition example

document.addEventListener('DOMContentLoaded', function() {
    // Initialize ScrollMagic
    var controller = new ScrollMagic.Controller();

    // Get device height
    var deviceHeight = window.innerHeight;

    // Create a scene for the features section
    var featureScene = new ScrollMagic.Scene({
        triggerElement: "#features",
        triggerHook: 0.1,
        duration: deviceHeight, // Duration is twice the device height
    })
    .setPin("#features") // Pin the features section
    .addTo(controller);

    // Recalculate on window resize
    window.addEventListener('resize', function() {
        deviceHeight = window.innerHeight;
        featureScene.duration(deviceHeight * 2);
    });

    // Animate feature items
    document.querySelectorAll('.feature-item').forEach((item, index) => {
        var tween = gsap.fromTo(item, 
            { scale: 3.5, opacity: 0 }, 
            { scale: 1, opacity: 1, duration: 1, delay: index * 0.3 }
        );

        new ScrollMagic.Scene({
            triggerElement: item,
            triggerHook: 0.8
        })
        .setTween(tween)
        .addTo(controller);
    });

    // Canvas animation
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

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
            const r = Math.floor(Math.random() * 100) + 100; // 100-199
            const g = Math.floor(Math.random() * 100); // 0-99
            const b = Math.floor(Math.random() * 155) + 100; // 100-254
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
        for (let i = 0; i < 10; i++) {
            curves.push(new Curve());
        }
        for (let i = 0; i < 20; i++) {
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
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        init();
    });
});