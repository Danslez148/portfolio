public class BacteriaCell extends Particle {
    private double angle;
    private double angularVelocity;
    private double friction;

    public BacteriaCell (double angle, double angularVelocity, double friction) {
        this.angle = angle;
        this.angularVelocity = angularVelocity;
        this.friction = friction;
    }

    public void divide() {
        // insert functionality
    }
    
    
    //this method needs change the position based on the total force and delta time and angle.
    public void update(double deltaTime) {
        //this needs to
        
        
        // 2. Add some random noise 
        Vector2D force = getRandomForce();
        force = totalForce.add(force);
    
        // 3. Over-damped dynamics: velocity = Force/(friction coeficient per unit length*?)
        velocity = force.multiply(1 / ((length+radius*2)));
        
        // 4. Update position: position += velocity * time
        position = position.add(velocity.multiply(deltaTime));
    
        double torque= (Math.random() - 0.5) * 100 * 2;

        // 7. Calculate angular velocity
        angularVelocity = (12 / (friction*Math.pow((length+radius*2), 3))) * torque;

        // 8. Update angle
        angle += angularVelocity*deltaTime;

        // 9. Normalize angle turn this into a method later we need to do this to make sure the angle is within 0 and 2PI
        while (angle < 0){
            angle += 2*Math.PI;
        }
        while (angle > 2*Math.PI) {
            angle -= 2*Math.PI;
        }
        //Reset total force here.
    }


    private Vector2D getRandomForce() {
        double magnitude = (Math.random()-0.5)*2*1000.0; 
        double randomAngle = Math.random() * 2 * Math.PI;
        return new Vector2D(
            magnitude * Math.cos(randomAngle),
            magnitude * Math.sin(randomAngle)
        );
    }
}
