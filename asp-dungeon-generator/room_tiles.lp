% % bridge facts ty daniel
% % --------------------
% room_type(Rx, Ry, T) :- rooms(Rx, Ry, T).

% %opening directions per room 

% opens(Rx, Ry, [direction]):-shapes(Rx, Ry, S), [direction]_open(S).

% % start and end
% is_start(Rx, Ry) :-start(Rx, Ry)
% is_end(Rx, Ry) :- end(Rx, Ry)

% % ---------------------

% constants
#const room_size = 9.           % must be odd so a clean midpoint exists
#const mid       = 4.           % room_size / 2, the door anchor column/row
#const inner_lo  = 1.           % first interior index
#const inner_hi  = 7.           % last interior index  (room_size - 2)

room_axes(0..room_size-1). %inspo from region_axes in level1region.lp

% for every region, there must be a tile s.t. it's in every room, and is a valid microcoordinate

tile_local(Rx,Ry,Tx,Ty) :- rooms(Rx,Ry,_), room_axes(Tx), room_axes(Ty).

% basically this just helps us define outer walls later on
perimeter(Rx,Ry,Tx,Ty) :- tile_local(Rx,Ry,Tx,Ty), Tx = 0.
perimeter(Rx,Ry,Tx,Ty) :- tile_local(Rx,Ry,Tx,Ty), Tx = room_size-1.
perimeter(Rx,Ry,Tx,Ty) :- tile_local(Rx,Ry,Tx,Ty), Ty = 0.
perimeter(Rx,Ry,Tx,Ty) :- tile_local(Rx,Ry,Tx,Ty), Ty = room_size-1.

% defines the exact opposite. A tile is considered interior if its in the inner parameters of the room. 
interior(Rx,Ry,Tx,Ty) :-
    tile_local(Rx,Ry,Tx,Ty),
    Tx >= inner_lo, Tx <= inner_hi, %if its in the interior indices, it must be an interior tile. intuitive
    Ty >= inner_lo, Ty <= inner_hi.

% up door
has_door(Rx,Ry,mid,0) :- %let me make sure the indices are right . edit: i think they are
    rooms(Rx,Ry,_),
    passable(Rx,Ry,Rx,Ry-1).

% down door
has_door(Rx,Ry,mid,room_size-1) :-
    rooms(Rx,Ry,_),
    passable(Rx,Ry,Rx,Ry+1).

% left door
has_door(Rx,Ry,0,mid) :-
    rooms(Rx,Ry,_),
    passable(Rx,Ry,Rx-1,Ry).

% right door
has_door(Rx,Ry,room_size-1,mid) :-
    rooms(Rx,Ry,_),
    passable(Rx,Ry,Rx+1,Ry).

#const trim = 3.   % mid - 1 edit: IM NOT STUPID I FORGOT TO CHANGE THIS NUMBER OKAY THIS NUMBER IS IMPORTANT FOR DEFINING SHAPES

% this part is just trying to define diamonds and ovals. bruh i can't idk what i'm doing wrong here (edit: see above note)

shape_masked(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,diamond),
    interior(Rx,Ry,Tx,Ty),
    Dx = Tx - mid, Tx >= mid, Dy = Ty - mid, Ty >= mid, Dx + Dy > trim.  % used manhattan distance bc clingo can't parse euclidean distance

shape_masked(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,diamond),
    interior(Rx,Ry,Tx,Ty),
    Dx = mid - Tx, Tx < mid, Dy = Ty - mid, Ty >= mid, Dx + Dy > trim.

shape_masked(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,diamond),
    interior(Rx,Ry,Tx,Ty),
    Dx = Tx - mid, Tx >= mid, Dy = mid - Ty, Ty < mid, Dx + Dy > trim.

shape_masked(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,diamond),
    interior(Rx,Ry,Tx,Ty),
    Dx = mid - Tx, Tx < mid, Dy = mid - Ty, Ty < mid, Dx + Dy > trim.


%there is definitely something wrong with my maths for the oval. guys what am i doing wrong :( (edit: see above above note)
shape_masked(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,oval),
    interior(Rx,Ry,Tx,Ty),
    Tx >= mid, Ty >= mid,
    Dx = Tx - mid, Dy = Ty - mid,
    Dx * Dx + Dy * Dy > trim * trim.

shape_masked(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,oval),
    interior(Rx,Ry,Tx,Ty),
    Tx < mid, Ty >= mid,
    Dx = mid - Tx, Dy = Ty - mid,
    Dx * Dx + Dy * Dy > trim * trim.

shape_masked(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,oval),
    interior(Rx,Ry,Tx,Ty),
    Tx >= mid, Ty < mid,
    Dx = Tx - mid, Dy = mid - Ty,
    Dx * Dx + Dy * Dy > trim * trim.

shape_masked(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,oval),
    interior(Rx,Ry,Tx,Ty),
    Tx < mid, Ty < mid,
    Dx = mid - Tx, Dy = mid - Ty,
    Dx * Dx + Dy * Dy > trim * trim.

% horizontal corridor strip — only mid row is open
corridor_floor(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,s_hor),
    interior(Rx,Ry,Tx,Ty),
    Ty = mid.

% vertical corridor strip — only mid column is open
corridor_floor(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,s_ver),
    interior(Rx,Ry,Tx,Ty),
    Tx = mid.

% cross — mid row and mid column both open
corridor_floor(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,cross),
    interior(Rx,Ry,Tx,Ty),
    Ty = mid.

corridor_floor(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,cross),
    interior(Rx,Ry,Tx,Ty),
    Tx = mid.

% t_tlr — top open, left open, right open (no down)
% horizontal bar + up stem
corridor_floor(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,t_tlr),
    interior(Rx,Ry,Tx,Ty),
    Ty = mid.

corridor_floor(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,t_tlr),
    interior(Rx,Ry,Tx,Ty),
    Tx = mid, Ty < mid.

% t_blr — bottom open, left open, right open (no up)
corridor_floor(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,t_blr),
    interior(Rx,Ry,Tx,Ty),
    Ty = mid.

corridor_floor(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,t_blr),
    interior(Rx,Ry,Tx,Ty),
    Tx = mid, Ty > mid.

% t_ltb — left open, top open, bottom open (no right)
corridor_floor(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,t_ltb),
    interior(Rx,Ry,Tx,Ty),
    Tx = mid.

corridor_floor(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,t_ltb),
    interior(Rx,Ry,Tx,Ty),
    Ty = mid, Tx < mid.

% t_rtb — right open, top open, bottom open (no left)
corridor_floor(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,t_rtb),
    interior(Rx,Ry,Tx,Ty),
    Tx = mid.

corridor_floor(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,t_rtb),
    interior(Rx,Ry,Tx,Ty),
    Ty = mid, Tx > mid.

% el_lt — left and top open
corridor_floor(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,el_lt),
    interior(Rx,Ry,Tx,Ty),
    Tx = mid, Ty <= mid.

corridor_floor(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,el_lt),
    interior(Rx,Ry,Tx,Ty),
    Ty = mid, Tx <= mid.

% el_rt — right and top open
corridor_floor(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,el_rt),
    interior(Rx,Ry,Tx,Ty),
    Tx = mid, Ty <= mid.

corridor_floor(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,el_rt),
    interior(Rx,Ry,Tx,Ty),
    Ty = mid, Tx >= mid.

% el_lb — left and bottom open
corridor_floor(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,el_lb),
    interior(Rx,Ry,Tx,Ty),
    Tx = mid, Ty >= mid.

corridor_floor(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,el_lb),
    interior(Rx,Ry,Tx,Ty),
    Ty = mid, Tx <= mid.

% el_rb — right and bottom open
corridor_floor(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,el_rb),
    interior(Rx,Ry,Tx,Ty),
    Tx = mid, Ty >= mid.

corridor_floor(Rx,Ry,Tx,Ty) :-
    shapes(Rx,Ry,el_rb),
    interior(Rx,Ry,Tx,Ty),
    Ty = mid, Tx >= mid.

% --- corridor masking ---
% Any interior tile of a corridor region that is NOT
% on the corridor_floor path gets masked as wall.
shape_masked(Rx,Ry,Tx,Ty) :-
    rooms(Rx,Ry,corridor),
    interior(Rx,Ry,Tx,Ty),
    not corridor_floor(Rx,Ry,Tx,Ty).


% this is basically where we assign tiles. 
% So priority of order goes door then wall then floor.
% i.e. we wanna deifne a door tile before it becomes a wall tile
% because we have a shape mask, that should be defined as a wall before it becomes a floor
% Everything else on the perimeter is wall, everything else interior is floor.

tile_obj(Rx,Ry,Tx,Ty,door) :- has_door(Rx,Ry,Tx,Ty).

tile_obj(Rx,Ry,Tx,Ty,wall) :- perimeter(Rx,Ry,Tx,Ty), not has_door(Rx,Ry,Tx,Ty).

tile_obj(Rx,Ry,Tx,Ty,wall) :- shape_masked(Rx,Ry,Tx,Ty).

tile_obj(Rx,Ry,Tx,Ty,floor) :- interior(Rx,Ry,Tx,Ty), not shape_masked(Rx,Ry,Tx,Ty).

#show tile_obj/5.
#show has_door/4.
