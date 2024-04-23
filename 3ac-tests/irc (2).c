void volchanger(void) {
  char i;
  int vol = 10;

  while(1) {
	i = getc();

	if(i == 'q') break;

	switch(i) {
    case '+':
	  vol++;
	  break;
    case '-':
	  vol--;
	  break;
    default:
	  printf("unrecognized command: %c\n", i);
	}
  }
}
