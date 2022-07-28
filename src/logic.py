import random, numpy
from typing import List, Dict

def get_info() -> dict:
    return {
        "apiversion": "1",
        "author": "sjc",  # TODO: Your Battlesnake Username
        "color": "#A671B6",  # TODO: Personalize
        "head": "tongue",  # TODO: Personalize
        "tail": "freckled",  # TODO: Personalize
    }


def choose_move(data: dict) -> str:
    my_snake = data["you"]      
    my_head = my_snake["head"] #tuple with coordinates  
    my_body = my_snake["body"]  

    board = data['board']
    board_height = board["height"]
    board_width = board["width"]

    possible_moves = ["up", "down", "left", "right"] 
    
    print(f"Current head: {my_head}")
  
    legal_moves=[] #hold all valid moves 
    for move in possible_moves:
      next_head = move_pos(move,my_head)
      #print("Move "+move)
      #print(next_head)
      
      #avoid walls
      if(out_of_bounds(board,next_head)):
        print("Removed "+move+" to avoid walls.")
        continue
  
      #avoid self and all others
      if(collide_snake(board["snakes"],next_head)):
        print("Removed "+move+" to avoid snakes.")
        continue
        
      legal_moves.append(move)

    print(f"Legal moves: {legal_moves}")
    #close snakes
    snake_count = close_snakes(board["snakes"],legal_moves,my_snake["length"],my_head) 

    #closest food
    food = data['board']['food']
    food_moves = moves_to_food(food,legal_moves,my_head)
    
    move = best_move(legal_moves,snake_count,food_moves)
    print(f"MOVE {data['turn']}: {move} picked from all valid options in {legal_moves}")
    print()
  
    return move

#returns a head that has moved in the direction specified by move
def move_pos(move: str, head: dict) -> dict:
  if move == "up":
    m = {"x":head["x"],"y":head["y"] + 1}
  if move =="down":
    m = {"x":head["x"],"y":head["y"] - 1}
  if move == "left":
    m = {"x":head["x"] - 1,"y":head["y"]}
  if move == "right":
    m = {"x":head["x"] + 1,"y":head["y"]}
  return m
  

#returns true if the head coords are out of bounds
def out_of_bounds(board: dict, head: dict) ->bool:

  if(head["x"]>=board["height"] or head["x"] <0):
    return True
  if(head["y"]>=board["width"] or head["y"] <0):
    return True
  return False

#returns true if the head coords will hit another snake, including ourselves
def collide_snake(snakes: dict, head:dict) -> bool:
  for s in snakes:
    body = s["body"] #list of coords
    if head in body:
      return True
  return False

#return moves in order of which has the least snakes
def close_snakes(snakes: dict, moves:List[dict], size: int, head:dict) -> dict:
  x=head["x"]
  y=head["y"]

  body_count = {
    "up":0,
    "down":0,
    "right":0,
    "left":0
  }
  l=3 #dimentions of square to check for snakes
  
  #add body 'points' to areas - lower index body part = more dangerous
  for s in snakes:
    body = s["body"]
    s_len = s["length"]
    for i in range (s_len):
      s_x= body[i]["x"]
      s_y= body[i]["y"]
      
      if ("up" in moves) and (s_y>y and s_y<=y+l and s_x>=x-l//2 and s_x<=x+l//2):
        body_count["up"]+=s_len-i
      if ("down" in moves) and (s_y<y and s_y>=y-l and s_x>=x-l//2 and s_x<=x+l//2):
        body_count["down"]+=s_len-i
      if ("right" in moves) and (s_y>=y-l//2 and s_y<=y+l//2 and s_x>x and s_x<=x+l):
        body_count["right"]+=s_len-i
      if ("left" in moves) and (s_y>=y-l//2 and s_y<=y+l//2 and s_x<x and s_x>=x-l):
        body_count["left"]+=s_len-i

  snake_count = dict(sorted(body_count.items(), key=lambda item: item[1]))
  print(f"Snake count: {snake_count}")
  return snake_count

#returns moves that move closest to food
def moves_to_food(food:List[dict],moves:List[dict],head:dict)->List[str]:
  if(len(food) == 0):
    return []
  #there is probably a better way to do this
  dist=10000
  closest={}
  x=head["x"]
  y=head["y"]
  for f in food:
    n_dist = (f["x"]-x)**2 + (f["y"]-y)**2
    if( n_dist < dist ):
      dist = n_dist
      closest = f

  ideal_moves=[]
  if closest["x"]>x:
    ideal_moves.append("right")
  if closest["x"]<x:
    ideal_moves.append("left")
  if closest["y"]>y:
    ideal_moves.append("up")
  if closest["y"]<y:
    ideal_moves.append("down")

  print(f"Move to closest food {closest}: {ideal_moves}")
  return (ideal_moves)

#takes all moves found and determines best one
def best_move(moves:List[str],snakes:dict,food:List[str])->str:
  #go through snakes and add smallest value of snakes but move present in moves
  best=[]
  for s_m in snakes:
    if s_m in moves:
      if len(best) == 0:
        best.append(s_m)
        continue
      if snakes[best[0]] == snakes[s_m]:
        best.append(s_m)

  #now we have a list of all smallest values
  print(f"Lowest snakes: {best}")
  best_move = best[0] #default
  #avoid getting trapped when facing wall and have two options
  
  #if for 1+ check if one is in food, return that one
  for m in best:
    if m in food:
      best_move= m
  return best_move
