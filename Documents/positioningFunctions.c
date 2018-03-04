void bottomToCenter(){
	/* 856 steps are needed to move  16.51 cm.
	*  16.51cm/4cm per rev = 4.1275 revolutions.
	*  4.1275 revs * 200 steps (full step) = 856 steps
	*/
	
}

INT16U calcSteps(int y){
	/* 90 steps are required to move 1cm. This is calculated from the following:
	* 1 Pulley has 20 teeth; Each tooth is seperated by 2mm. 
	* Assuming 50% contact (timing belt to pulley) that is 10 teeth.
	* 10 teeth * 2mm = 2cm in half a revolution.
	* 1 revolution is therefore 4cm.
	* 1 Revolution has 200 steps (full step) so 1cm is 1/4 of a revolution (90 steps)
	*/ 
	
    INT16U numStepsNeeded=0;

    //90 steps for 1 cm
   
    if (y!=0){
        numStepsNeeded = 90* abs(y);
    }

    return numStepsNeeded;
}

 enum Direction calcDirection(int y){
	/* This function determines the correct direction given a y. 
	* If y is negative, the board should be moving downwards; done
	* by rotating the motor clockwise. If y is positive, board
	* should move upwards and thus counterclockwise.
	*/
    if (y<0){
        return cw;
    }
    else{
        return ccw;
    }
}
