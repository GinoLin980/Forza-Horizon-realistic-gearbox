# Page for Forza Horizon Realistic Gearbox

## This is a README for what I've learned by building this website.

### HTML

Pretty easy, nothing new learned
---

### CSS

Use `#ElementId` and `#ElementId Mark` to specify a certain element's style.
`rem` is a font unit that varies on the default `font-size`

Default `font-size` can be set using:
```CSS
@media screen and (<min-width/max-width>: <n>px) {
    html {
        font-size: <n>px; 
    }
}
```
To let items be aligned with vertical center line:
```CSS
#Element {
    margin: 0 auto;
}
```

To achieve gradient color on texts:
``` CSS
#Element Mark{
    color: transparent;
    background: linear-gradient(to right, #71a7e4, #9c32ff, #e15d9f);
    -webkit-background-clip: text;
    background-clip: text;
}
```

To make texts glow:
```CSS
#Element Mark{
        text-shadow: 0 0 0.5px rgba(0, 0, 0, 0.163), 0 0 10px rgba(255, 255, 255, 0.3), 0 0 15px rgba(255,  255, 255, 0.2), 0 0 45px rgba(255, 0, 221, 0.152);
}
```

To set element invisible:
```CSS
#Element {
    opacity: 0;
}
```

Fade in animation:
```CSS
@keyframes fadeInAnimation {
    0% { opacity: 0; }
    100% { opacity: 1; }
}

#Element {
    animation: fadeInAnimation ease <n>s forwards;
}
```
---

