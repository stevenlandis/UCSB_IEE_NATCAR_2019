
const int resolution1 = 1800;
const double microtoseconds = 1 * pow(10,-6);

double distancex(double x){ //inches
  return (x/resolution1);
}

double distancey(double y){
  return (y/resolution1);
}

double velocityx(double distancex, long timeInterval){ //meter/sec
  return (distancex*2.54)/(timeInterval * microtoseconds);
}

double velocityy(double distancey, long timeInterval){
  return (distancey*2.54)/(timeInterval * microtoseconds); 
}

double accelerationx(double velocityax, double velocitybx, long timeInterval){ //meter/sec^2
  double changeinx = abs(velocityax - velocitybx);
  return changeinx/(timeInterval * microtoseconds);
}

double accelerationy(double velocityay, double velocityby, long timeInterval){
  double changeiny = abs(velocityay - velocityby);
  return changeiny/(timeInterval * microtoseconds);
}
