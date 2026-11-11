// describing employees
// SCHDAN066
// Daniel Schlesinger
// 15 September 2023

import java.util.*;

public class Employee {
   private String name;
   private String uid;
   private List<Shift> shifts = new ArrayList<Shift>();
   private CalendarTime start;
   private CalendarTime finish;
   private boolean SignedIn = false;
   
   public Employee(String name, String uid) {
      this.name = name;
      this.uid = uid;
   }
   
   public String name() {
      return name;
   }
   
   public String UID() {
      return uid;
   }
   
   public void signIn(Date d, Time t) {
      CalendarTime start = new CalendarTime(d, t);
      this.start = start;
      SignedIn = true;
   }
   
   public void signOut(Date d, Time t) {
      CalendarTime finish = new CalendarTime(d, t);
      this.finish = finish;
      Shift addShift = new Shift(this.start, this.finish);
      shifts.add(addShift);
      SignedIn = false;
   }
   
   public boolean present() {
      return SignedIn;
   }
   
   public boolean worked(Date d) {
      boolean worked = false;
      for (int i = 0; i<shifts.size(); i++) {
         if (shifts.get(i).includesDate(d)) {
            worked = true;
         }
      }
      return worked;
   }
   
   public boolean worked(Week w) {
      boolean worked = false;
      for (int i = 0; i<shifts.size(); i++) {
         if (shifts.get(i).inWeek(w)) {
            worked = true;
         }
      }
      return worked;
   }
   
   public List<Shift> get(Date d) {
      List<Shift> dateShifts = new ArrayList<Shift>();
      for (int i = 0; i<shifts.size(); i++) {
         if (shifts.get(i).includesDate(d)) {
            dateShifts.add(shifts.get(i));
         }
      }
      return dateShifts;
   }
   
   public List<Shift> get(Week w) {
      List<Shift> weekShifts = new ArrayList<Shift>();
      for (int i = 0; i<shifts.size(); i++) {
         if (shifts.get(i).inWeek(w)) {
            weekShifts.add(shifts.get(i));
         }
      }
      return weekShifts;
   }
   
   public Duration hours(Week w) {
      Duration cumulative = new Duration("minute", 0);
      List<Shift> weekShifts = this.get(w);
      for (int i = 0; i<weekShifts.size(); i++) {
         cumulative = cumulative.add(weekShifts.get(i).length());
      }
      return cumulative;
   }
}