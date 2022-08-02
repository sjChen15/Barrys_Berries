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
    head_x = my_snake["head"]["y"]
    head_y = my_snake["head"]["x"]
    my_head = (head_x,head_y) #tuple with coordinates
    my_body = my_snake["body"]  
  
    food = data['board']['food']
  
    board = data['board']
    board_height = board["height"]
    board_width = board["width"]

    grid = [[0 for x in range(board_width)] for y in range(board_height)]
    snake_heads = [] #list of heads of snakes
    fill_snakes(grid,snake_heads,board["snakes"])
    #print_grid(grid)
    snake_heads.remove(my_snake["head"])
    print(f"Heads of snakes: {snake_heads}")
  
    possible_moves = ["up", "down", "left", "right"] 
    
    print(f"Current head: {my_head}")
  
    legal_moves=[] #hold all valid moves 
    for move in possible_moves:
      
      if move == "up" and head_x+1<board_width and grid[head_x+1][head_y] == 0:
        legal_moves.append(move)
      if move =="down" and head_x-1>=0 and grid[head_x-1][head_y] == 0:
        legal_moves.append(move)
      if move == "left" and head_y-1>=0 and grid[head_x][head_y-1] == 0:
        legal_moves.append(move)
      if move == "right" and head_y+1<board_height and grid[head_x][head_y+1] == 0:
        legal_moves.append(move)
      

    print(f"Legal moves: {legal_moves}")

    #best moves by bsf
    serach_moves = dfs_moves(legal_moves,grid,my_head)
    print(f"dfs_moves: {serach_moves}")

    #find potential head to head hits
    head_moves = head_to_head(legal_moves,snake_heads)
    #closest food
    food_moves = moves_to_food(food,legal_moves,my_head)
  
    move = best_move(legal_moves,serach_moves,food_moves,my_snake)
    print(f"MOVE {data['turn']}: {move} picked from all valid options in {legal_moves}")
    print()
  
    return move


def print_grid(grid:List[List[int]])->None:
  l = len(grid)
  for i in range(l):
    print(grid[l-i-1])

    
def fill_snakes(grid:List[List[int]],heads:List[dict],snakes: dict) -> None:
  for s in snakes:
    body = s["body"] #list of coords
    for pos in body:
      #print(pos)
      if pos == body[0]: #head of snake
        heads.append(pos)
      grid[ pos["y"] ][ pos["x"] ] = 1

#return moves in order of which has most space up to size of snake
def dfs_moves(moves:List[dict], grid: List[List[int]], head:tuple) -> dict:
  x=head[0]
  y=head[1]

  count = {
    "up":0,
    "down":0,
    "right":0,
    "left":0
  }
  
  for m in count:
    if m not in moves:
      
      continue
    looked = [[0 for x in range(len(grid))] for y in range(len(grid))]
    if m=="up":
      print(f"counting for {m}")
      count[m] = dfs((x+1,y),grid,looked)
    if m=="down":
      print(f"counting for {m}")
      count[m] = dfs((x-1,y),grid,looked)
    if m=="left":
      print(f"counting for {m}")
      count[m] = dfs((x,y-1),grid,looked)
    if m=="right":
      print(f"counting for {m}")
      count[m] = dfs((x,y+1),grid,looked)

  return dict(sorted(count.items(), key=lambda item: item[1], reverse=True))

def dfs(p:tuple,grid:List[List[int]],looked:List[List[int]]) ->int:
  l=len(grid)
  if p[0] >=l or p[1] >=l or p[0] <0 or p[1]<0:
    #print("here 1")
    return 0
  if looked[p[0]][p[1]] ==1:
    #print("here 2")
    return 0
  if grid[p[0]][p[1]] == 1:
    #print("here 3")
    return 0
    
  looked[p[0]][p[1]] = 1
  
  #see if up down left and right have been looked for/in range
  look_up = 1 if(p[1]+1 < l and looked[p[0]][p[1]+1] == 0) else 0
  look_down = 1 if(p[1]-1 >= 0 and looked[p[0]][p[1]-1] == 0) else 0
  look_right = 1 if (p[0]+1 < l and looked[p[0]+1][p[1]] == 0) else 0
  look_left = 1 if(p[0]-1 >=0 and looked[p[0]-1][p[1]] == 0) else 0
  
  sum = 1
  
  sum += dfs((p[0],p[1]+1),grid,looked) if look_up else 0
  sum += dfs((p[0],p[1]-1),grid,looked) if look_down else 0
  sum += dfs((p[0]+1,p[1]),grid,looked) if look_right else 0
  sum += dfs((p[0]-1,p[1]),grid,looked) if look_left else 0
  
  return sum

#returns list of legal moves that don't have bad head to head collisions
def head_to_head(moves:List[dict],heads: List[dict]) -> List[str]:
#find possible head to head collisions and only remove if the snake is >= 
  return ["up"]


  
#returns moves that move closest to food
def moves_to_food(food:List[dict],moves:List[dict],head:tuple)->List[str]:
  if(len(food) == 0):
    return []
  #there is probably a better way to do this
  dist=10000
  closest={}
  x=head[1]
  y=head[0]
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

#bfs to find move with most space up to its own size and closer to food if possible
def best_move(moves:List[str], bfs:dict, food:List[str],me:dict)->str:
  #go through bfs and add smallest value of bfs val but move present in moves
  best=[]
  for s_m in bfs:
    if s_m in moves:
      if bfs[s_m] >= me["length"]:  
        best.append(s_m)

  #no spaces bigger than snake size
  if(len(best) == 0):
    for s_m in bfs:
      if s_m in moves:
        if len(best) == 0:
          best.append(s_m)
        elif best[0] == bfs[s_m]:  
          best.append(s_m)
          
  print(f"Best moves: {best}")
  #now we have a list of all smallest values
  if(len(best) == 0):
    return "up" #if there are no moves just return up

  best_move = best[0] #default
  if(len(best) == 1):
    return best_move
    
  #look into future for each of the best moves and choose 
  #elif:
    #for


  #if for 1+ check if one is in food, return that one
  for m in best:
    if m in food:
      return m

  return best_move
