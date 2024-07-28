document.addEventListener('DOMContentLoaded', function() {
    var controller = new ScrollMagic.Controller();
    var deviceHeight = window.innerHeight;
    function isMobile() {
        let check = false;
        (function(a){if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4))) check = true;})(navigator.userAgent||navigator.vendor||window.opera);
        return check;
      };
  
      if (isMobile()) {
        document.body.classList.add('mobile');
        document.getElementById('features').style.height = '200vh';
        document.querySelector('#features h2').style.fontSize = '2.5em';
        document.querySelector('#features h3').style.fontSize = '1.2em';
        document.querySelector('#features p').style.fontSize = '1em';
        document.querySelector('#setup-instructions').style.height = 'auto';
        document.querySelector('#main').style.height = '100vh';
      }

    // Create the feature scene
    var featureScene = new ScrollMagic.Scene({
        triggerElement: "#features",
        triggerHook: isMobile() ? 0.2 : 0,
        duration: isMobile() ? '75%' : deviceHeight,
        offset: isMobile() ? 10 : 0
      })
      .setPin("#features", {pushFollowers: true})
      .addTo(controller);

  
    // Animate feature items
    document.querySelectorAll('.feature-item').forEach((item, index) => {
      var tween = gsap.fromTo(item, 
        { scale: isMobile() ? 2.5 : 3.5, opacity: 0 }, 
        { scale: 1, opacity: 1, delay: index * 0.4 }
      );
  
      new ScrollMagic.Scene({
        triggerElement: item,
        triggerHook: isMobile() ? 1.4 : 0.8,
      })
      .setTween(tween)
      .addTo(controller);
    });
  
    // Canvas setup
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
        for (let i = 0; i < (isMobile() ? 5 : 10); i++) {
          curves.push(new Curve());
        }
        for (let i = 0; i < (isMobile() ? 10 : 20); i++) {
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
        if (!isMobile()) {
            resizeCanvas();
            init();}
      });
    });