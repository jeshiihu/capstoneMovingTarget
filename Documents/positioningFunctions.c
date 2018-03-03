INT16U calcSteps(int y){
    INT16U numStepsNeeded=0;

    //90 steps for 1 cm
   
    if (y!=0){
        numStepsNeeded = 90* abs(y);
    }

    return numStepsNeeded;
}

 enum Direction calcDirection(int y){
    if (y<0){
        return ccw;
    }
    else{
        return cw;
    }
}
