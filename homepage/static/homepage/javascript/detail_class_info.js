var events = document.querySelectorAll('[id^="event-card-"]');
for (let i = 0; i < events.length; i++) {
    events[i].onmouseover = function() {
        this.style.backgroundColor = '#A7CCB8';
        this.style.cursor = 'zoom-in';
    }

    events[i].onmouseout = function() {
        this.style.backgroundColor = '';

    }
}

var trash_icons = document.querySelectorAll('[id^="trash-"]');
for (let k = 0; k < trash_icons.length; k++) {
    trash_icons[k].onmouseover = function() {
        this.style.cursor = 'pointer';
        this.style.fontSize = "large";
        this.style.opacity = 1;
    }

    trash_icons[k].onmouseout = function() {
        this.style.fontSize = "medium";
        this.style.opacity = 0.6;
    }
}
