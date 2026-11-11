public class Bacteria {
    private Vector2D position; // possition
    private Vector2D velocity; // where it is actually moving. Changes due to noise.
    private double angle; // Where bacteria wants to go.
    private double motilityForce; 
    private double friction;
    private double angularVelocity; // rate of rotation
    private double length; // length of cell
    private double radius;
    private double critLength;
    
    public Bacteria(double startX, double startY, double motilityForce) {
        this.position = new Vector2D(startX, startY);
        this.velocity = new Vector2D(0, 0); 
        this.angle = Math.random() * 2 * Math.PI; // Random initial direction in radians. Multiply random number (0-1) by pi (0-pi) and then multiply by 2 (0-2pi) covering full range of circle.
        this.motilityForce = motilityForce;
        this.friction = 200.0; // Cahnge to what is necesary.
        this.length= 1;
        this.radius= 0.5;
        this.critLength = 5;
    }

    public void update(double deltaTime) {
        // 1. Calculate motility force (along bacteria's direction)
        Vector2D motilityVector = new Vector2D(
            motilityForce * Math.cos(angle),
            motilityForce * Math.sin(angle)
        );
        
        // 2. Add some random noise 
        Vector2D force = getRandomForce();
        force = motilityVector.add(force);
    
        // 3. Over-damped dynamics: velocity = Force/(friction coeficient per unit length*?)
        velocity = force.multiply(1 / (friction*(length+radius*2)));
        
        // 4. Update position: position += velocity * time
        position = position.add(velocity.multiply(deltaTime));
        
        // 5. calculate new length
        length += calcGrowthRate() * 3.5 * (deltaTime / 3600);
        
        
        
        // 6. Get torque not sure how to calculate torque
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

    }

    private Vector2D getRandomForce() {
        double magnitude = (Math.random()-0.5)*2*1000.0; 
        double randomAngle = Math.random() * 2 * Math.PI;
        return new Vector2D(
            magnitude * Math.cos(randomAngle),
            magnitude * Math.sin(randomAngle)
        );
    }

    private double calcArea(){
        double area = Math.PI * Math.pow(radius, 2);
        area += 2 * radius * length; 
        return area;
    }

    private double calcAvgArea(){
        double area= Math.PI * Math.pow(radius, 2) + (3 / 2) * radius * length; 
        return area;
    }

    private double monodFunction(double nutrient_density){
        
        return nutrient_density / (1 + nutrient_density);
    }

    private double calcGrowthRate(){
        return (calcArea() / calcAvgArea()) * monodFunction(0.5);
    }

   

    public Vector2D getPosition() {
        return position;
    }
    
    public double getAngle() {
        return angle;
    }
    
    // Convert angle to degrees for easier reading
    public double getAngleDegrees() {
        return Math.toDegrees(angle) % 360;
    }

    public double getSpeed() {
        return velocity.magnitude();
    }

    public double getLength() {
        return length;
    }




    public boolean shouldDivide(double deltaTime) {
        if (length >= critLength) { 
            return true;
        }
        return false;
    }

    public void setLength(double length) {
        this.length = length;
    }

    public void setAngle(double angle) {
        this.angle = angle;
    }

    public Bacteria[] divide() {
        Bacteria daughter1 = new Bacteria(position.x, position.y, motilityForce);
        daughter1.setLength(this.getLength()/2);
        daughter1.setAngle(Math.random() * 2 * Math.PI);
        //Bacteria daughter2 = new Bacteria(position.x, position.y, motilityForce);
        //daughter2.setLength(this.getLength()/2);
        //daughter2.setAngle(Math.random() * 2 * Math.PI);

        //this.setAngle(Math.random() * 2 * Math.PI);
        this.setLength(this.getLength()/2);

        return new Bacteria[] {daughter1};
    }


}
