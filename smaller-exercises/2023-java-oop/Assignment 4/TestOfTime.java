import org.junit.Assert;
import static org.junit.Assert.*;
import org.junit.Before;
import org.junit.Test;


public class TestOfTime {


   /** Fixture initialization (common initialization
    *  for all tests). **/
   @Before public void setUp() {
   }


   /** A test that always fails. **/
   @Test public void defaultTest() {
      /** Time object storing correctly **/
      Time testTime = new Time(6, 30);
      Assert.assertEquals("06:30:00", testTime.toString());
      
      /** Time subtraction working correctly **/
      Time testTime2 = new Time(3, 30);
      Duration expectedDuration = new Duration("hour", 3);
      Assert.assertTrue(testTime.subtract(testTime2).compareTo(expectedDuration) == 0);
      
      /** Checking self subtraction is 0 **/
      Duration noDuration = new Duration("hour", 0);
      Assert.assertTrue(testTime.subtract(testTime).compareTo(noDuration) == 0);
      
      Duration testingDuration = new Duration(TimeUnit.HOUR, 1).add(new Duration(TimeUnit.MINUTE, 14));
      /** intValue for millisecond **/
      Assert.assertEquals(testingDuration.intValue("millisecond"), 4440000);
      
      /** intValue for second **/
      Assert.assertEquals(testingDuration.intValue("second"), 4440);
      
      /** intValue for minute **/
      Assert.assertEquals(testingDuration.intValue("minute"), 74);
      
      /** intValue for hour **/
      Assert.assertEquals(testingDuration.intValue("hour"), 1);
   }
}
