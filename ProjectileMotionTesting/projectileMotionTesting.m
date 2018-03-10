%%% ECE 492 - Group 3 Projectile Motion Testing
%%% Created by: Tyler Mathieu
%%% Last Edited: March 5, 2018
%%% Based on code from https://www.mathworks.com/help/matlab/ref/quiver3.html

function [] = projectileMotionTesting(xPos, yPos, zPos, xVel, yVel, zVel)
%This function takes our data from the raspberryPi and plots those 
%results, comparing them to a perfect parabola
%Values are currently hardcoded, will be changed throughout testing phase

zVel = 10; % velocity constant
g = -9.81; % acceleration constant
distance = 3.66; %total travel distance of ball

tend = (distance-xPos)/xVel;
t = 0:.1:tend;
z = zVel*t + 1/2*g*t.^2;

vx = xVel;
x = vx*t;
vy = yVel;
y = vy*t;

u = gradient(x);
v = gradient(y);
w = gradient(z);
scale = 0;

figure
quiver3(x,y,z,u,v,w,scale)
view([70,18])

end

