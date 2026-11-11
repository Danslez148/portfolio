%constants 

#const x_regions = 6.
#const y_regions = 6.
#const n_regions = x_regions * y_regions.
#const n_rooms   = 12.
#const n_special = 3.
#const n_normal  = n_rooms - n_special.
#const n_corrs   = (x_regions * y_regions) - n_rooms.


% raxes defines all valid region coordinates.
% types_of_room is used in later rules.

raxes(0..x_regions-1, 0..y_regions-1).
types_of_room(special; normal; corridor).
special_type(tomb_of_fear; chamber_of_death; pit_of_flame).


% Special rooms are placed one per named type, then derived into the rooms predicate. Normal and corridor counts are exact.

1{ special_rooms(Rx,Ry,S) : raxes(Rx,Ry) }1 :- special_type(S).
rooms(Rx,Ry,special)   :- special_rooms(Rx,Ry,S).
n_normal{ rooms(Rx,Ry,normal)   : raxes(Rx,Ry) }n_normal.
n_corrs { rooms(Rx,Ry,corridor) : raxes(Rx,Ry) }n_corrs.


% Rooms get room shapes, corridors get corridor shapes.
% Shape determines which walls have openings 

room_shapes(rectangular; oval; diamond; open).
corridor_shapes(cross; s_hor; s_ver;
                t_tlr; t_ltb; t_blr; t_rtb;
                el_lt; el_rt; el_lb; el_rb).

1{ shapes(Rx,Ry,S) : room_shapes(S)     }1 :- rooms(Rx,Ry,special).
1{ shapes(Rx,Ry,S) : room_shapes(S)     }1 :- rooms(Rx,Ry,normal).
1{ shapes(Rx,Ry,S) : corridor_shapes(S) }1 :- rooms(Rx,Ry,corridor).

% Start is any region. The objective is one named special type, and end is derived from whichever region holds that type.

1{ start(Rx,Ry)      : raxes(Rx,Ry)      }1.
1{ objective_room(O) : special_type(O)    }1.
end(Rx,Ry) :- special_rooms(Rx,Ry,S), objective_room(S).


% Two regions are adjacent if they differ by 1 in either axis.

adjacent_region(Rx,Ry,Rx+1,Ry) :- raxes(Rx,Ry), raxes(Rx+1,Ry).
adjacent_region(Rx,Ry,Rx,Ry+1) :- raxes(Rx,Ry), raxes(Rx,Ry+1).
adjacent_region(Rx,Ry,Ru,Rv)   :- adjacent_region(Ru,Rv,Rx,Ry).


% All room shapes open on all sides.
% Corridor shapes only appear in directions their shape opens.

up_open(cross; s_ver; t_tlr; t_ltb; t_rtb;
        el_lt; el_rt;
        rectangular; oval; diamond; open).

down_open(cross; s_ver; t_blr; t_ltb; t_rtb;
          el_lb; el_rb;
          rectangular; oval; diamond; open).

left_open(cross; s_hor; t_tlr; t_ltb; t_blr;
          el_lt; el_lb;
          rectangular; oval; diamond; open).

right_open(cross; s_hor; t_tlr; t_blr; t_rtb;
           el_rt; el_rb;
           rectangular; oval; diamond; open).


% No region gets two types.
% No region gets two special types.
% Normal rooms cannot be adjacent to each other or to special
% corridors must separate rooms.

:- rooms(Rx,Ry,T1), rooms(Rx,Ry,T2), T1 != T2.
:- special_rooms(Rx,Ry,S1), special_rooms(Rx,Ry,S2), S1 != S2.
:- rooms(Rx,Ry,normal), rooms(Ru,Rv,normal),
   adjacent_region(Rx,Ry,Ru,Rv).
:- rooms(Rx,Ry,normal), rooms(Ru,Rv,special),
   adjacent_region(Rx,Ry,Ru,Rv).


% No region gets two shapes.

:- shapes(Rx,Ry,S1), shapes(Rx,Ry,S2), S1 != S2.


% Adjacent regions must have matching openings.
% If a region opens toward its neighbour, the neighbour must open back. If it doesn't open, the neighbour must not either.

:- shapes(Rx,Ry,S1), shapes(Rx+1,Ry,S2),
   right_open(S1), not left_open(S2).
:- shapes(Rx,Ry,S1), shapes(Rx+1,Ry,S2),
   not right_open(S1), left_open(S2).

:- shapes(Rx,Ry,S1), shapes(Rx,Ry+1,S2),
   down_open(S1), not up_open(S2).
:- shapes(Rx,Ry,S1), shapes(Rx,Ry+1,S2),
   not down_open(S1), up_open(S2).

:- rooms(Rx,Ry,special), rooms(Ru,Rv,special),
   adjacent_region(Rx,Ry,Ru,Rv).

% move_to simulates walking the region graph step by step.
% The no-revisit condition prevents cycles.
% completed_at records which step the exit was reached.
% The dungeon is valid only if completed, and only if the path is long enough to be interesting.

passable(Rx,Ry,Rx+1,Ry) :-
    shapes(Rx,Ry,S1), shapes(Rx+1,Ry,S2),
    right_open(S1), left_open(S2).
passable(Rx,Ry,Rx,Ry+1) :-
    shapes(Rx,Ry,S1), shapes(Rx,Ry+1,S2),
    down_open(S1), up_open(S2).
passable(Rx,Ry,Ru,Rv) :- passable(Ru,Rv,Rx,Ry).

step(1..n_regions).

move_to(Rx,Ry,0) :- start(Rx,Ry).
move_to(Rx,Ry,S) :-
    step(S),
    move_to(Px,Py,S-1),
    passable(Px,Py,Rx,Ry),
    0{ move_to(Rx,Ry,0..S-1) }0.

completed_at(S) :- end(Rx,Ry), move_to(Rx,Ry,S).
completed       :- completed_at(S).

:- not completed.
:- completed_at(S), S < 3.

#show rooms/3.
#show shapes/3.
#show start/2.
#show end/2.
#show objective_room/1.
#show special_rooms/3.
#show completed_at/1.
