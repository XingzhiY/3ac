void check_range(int temperature_c) {
  if(temperature_c < 0) 
	printf("freezing");
  else if (temperature_c > 100) {
	printf("boiling");
  } else {
	printf("operating range");
  }
}
