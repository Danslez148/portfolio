

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.io.*;
/*
 * force calculation class to apply and calculate repulsive forces particles experience
 */
class ForceCalculator {
    double BacteriaBacteriaElastic;
    double BacteriaEPSElastic;
    double EPSEPSElastic;

    public ForceCalculator(SimulationConfig config){
        this.BacteriaBacteriaElastic=config.getBacteriaBacteriaElastic();
        this.BacteriaEPSElastic=config.getBacteriaToEPSElasticModulus();
        this.EPSEPSElastic=config.getEPSToEPSElasticModulus();
    }
    /*
     * callable method that takes in a list of particles to alter and a list of particles they can interact with.
     * calls applyrepulsion on these particle combinations.
     */
    public void calculateRepulsiveForces(List<Particle> particles, List<Particle> neighbors) {
        for (Particle p1 : particles) {
            for (Particle p2 : neighbors) {
                if (p1 == p2) continue;
                
                double quickDist = p1.getPosition().distance(p2.getPosition());
                double maxInteractionDist = p1.getRadius() + p2.getRadius() + Math.max(p1.getLength(), p2.getLength());
                
                if (quickDist > maxInteractionDist) continue;
                
                applyRepulsion(p1, p2);
            }
        }
    }
    /*
     * Calculates the repulsion forces for 2 particles and applies them to p1.
     * calculates closestpoints and force magnitude and calls addforces at point on the particle that is being affected.
     */
    private void applyRepulsion(Particle p1, Particle p2) {
        Vector2D[] ends1 = particleEndpoints(p1);
        Vector2D[] ends2 = particleEndpoints(p2);

        ClosestPoints cp = segmentClosestPoints(ends1[0], ends1[1], ends2[0], ends2[1]);
        
        double overlap = Math.max(p1.getRadius() + p2.getRadius() - cp.distance,0);// biggestOverlap);
        
        

        double elasticModulus = getElasticModulus(p1, p2);
        double forceMagnitude = elasticModulus * Math.sqrt(p1.getRadius() + p2.getRadius()) * Math.pow(overlap, 1.5);
        
        Vector2D contactDirection = cp.pointOnSeg2.subtract(cp.pointOnSeg1);
        
        Vector2D force = contactDirection.normalize().multiply(-forceMagnitude);
        
        p1.addForceAtPoint(force, cp.pointOnSeg1);
    }

    /*
     * finds the particles endpoints which is the two furthest points along the central line of the particle - the diameter
     * of the particle to account for the endcaps.
     */
    private Vector2D[] particleEndpoints(Particle p) {
        if (p instanceof BacteriaCell) {
            Vector2D dir = new Vector2D(Math.cos(p.getAngle()), Math.sin(p.getAngle())).multiply(p.getLength() / 2.0-p.getRadius()*2);
            Vector2D A = p.getPosition().add(dir);
            Vector2D B = p.getPosition().subtract(dir);
            return new Vector2D[]{A, B};
        } else {
            Vector2D pos = p.getPosition();
            return new Vector2D[]{pos, pos};
        }
    }
    /*
     * returns the elastic modulus of the interaction. have to add a new check for every interaction posible.
     */
    private double getElasticModulus(Particle p1, Particle p2) {
        if (p1 instanceof BacteriaCell && p2 instanceof BacteriaCell) return BacteriaBacteriaElastic;
        if (p1 instanceof EPSParticle && p2 instanceof EPSParticle) return EPSEPSElastic;
        return BacteriaEPSElastic;
    }

    /*
     * finds the closest point along a line given the two endpoints on that line.
     */
    public ClosestPoints segmentClosestPoints(Vector2D p1, Vector2D q1, Vector2D p2, Vector2D q2) {
        Vector2D u = q1.subtract(p1);
        Vector2D v = q2.subtract(p2);
        Vector2D w = p1.subtract(p2);
        double a = u.dot(u);
        double b = u.dot(v);
        double c = v.dot(v);
        double d = u.dot(w);
        double e = v.dot(w);
        double D = a*c - b*b;

        double sN, sD = D, tN, tD = D;

        if (D < 1e-8) {
            sN = 0.0; sD = 1.0;
            tN = e; tD = c;
        } else {
            sN = (b*e - c*d);
            tN = (a*e - b*d);
            if (sN < 0) { sN = 0; tD = D; tN = e; }
            else if (sN > sD) { sN = sD; tD = D; tN = e + b; }
        }

        if (tN < 0) {
            tN = 0;
            if (-d < 0) sN = 0;
            else if (-d > a) sN = sD;
            else { sN = -d; sD = a; }
        } else if (tN > tD) {
            tN = tD;
            if ((-d + b) < 0) sN = 0;
            else if ((-d + b) > a) sN = sD;
            else { sN = (-d + b); sD = a; }
        }

        double sc = Math.abs(sN) < 1e-8 ? 0.0 : sN / sD;
        double tc = Math.abs(tN) < 1e-8 ? 0.0 : tN / tD;

        Vector2D pointOnSeg1 = p1.add(u.multiply(sc));
        Vector2D pointOnSeg2 = p2.add(v.multiply(tc));

        ClosestPoints cp = new ClosestPoints();
        cp.pointOnSeg1 = pointOnSeg1;
        cp.pointOnSeg2 = pointOnSeg2;
        cp.distance = pointOnSeg1.distance(pointOnSeg2);
        return cp;
    }

    public static class ClosestPoints {
        public Vector2D pointOnSeg1;
        public Vector2D pointOnSeg2;
        public double distance;
    }
}
