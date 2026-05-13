const myText = new AutoTyping({
    id: 'typewriter', //Your HTML element id (string) - REQUIRED
    typeSpeed: 100, //Type speed in milliseconds (number) - OPTIONAL
    cursor: '-', //,
    textColor: '#dc3545',
    // deleteSpeed: 100, //Speed in milliseconds
    typeText: ['سلام دنیا!', '...خوش آمدید', ] //Your text (array with strings)
  }).init();