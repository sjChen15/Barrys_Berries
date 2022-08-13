from curses.panel import top_panel
from typing import List
import json,random,numpy

def get_info() -> dict:
    return {
        "apiversion": "1",
        "author": "sjc",
        "color": "#A671B6",
        "head": "tongue",
        "tail": "freckled",  
    }


def choose_move(data: dict) -> str:
    my_snake = data["you"]     
    head_x = my_snake["head"]["y"]
    head_y = my_snake["head"]["x"]
    my_head = (head_x,head_y) #tuple with coordinates
    my_body = my_snake["body"]  
  
    board = data['board']
    board_height = board["height"]
    board_width = board["width"]
    food = board['food']

    grid = [[0 for x in range(board_width)] for y in range(board_height)]
    
    #read and write old food
    old_food = wr_old_food(food)

    longest=fill_snakes(grid, board,old_food)
    #print_grid(grid)

    possible_moves = ["up", "down", "left", "right"] 
  
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

    #best moves by dfs with dumb dfs
    serach_moves = dfs_moves(legal_moves,grid,my_head)
    print(f"dfs_moves: {serach_moves}")
    
    #find potential head to head hits
    other_snakes = board["snakes"]
    other_snakes.remove(my_snake)
    head_moves=[]
    if(len(other_snakes) !=0):
      head_moves = head_to_head(legal_moves,other_snakes,my_snake)

    #closest food
    food_moves = moves_to_food(food,legal_moves,my_head)
    print(f"All food: {food}")

    move = best_move(legal_moves,serach_moves[0],serach_moves[1],head_moves,food_moves,my_snake,longest)
    print(f"MOVE {data['turn']}: {move} picked from all valid options in {legal_moves}")
    print()
  
    return move


def print_grid(grid:List[List[int]])->None:
  l = len(grid)
  for i in range(l):
    print(grid[l-i-1])

#returns last turn's food
def wr_old_food(food:List[dict])->List[dict]:
  f = open("old_food.json", "w")

  #read
  old_food = json.load(f)["food"]
  to_dict = {"food":food}
  
  #write
  json.dump(to_dict, f)
  f.close()

  return old_food

#fills board and returns longest snake size
def fill_snakes(grid:List[List[int]],board: dict,old_food:List[dict]) -> int:
  sizes = []
  for s in board["snakes"]:
    body = s["body"] #list of coords
    sizes.append(s["length"])
    for pos in body:
      #print(pos)

      #allow for tail chasing
      if(pos != body[len(body)-1] and body[0] not in old_food):
        grid[ pos["y"] ][ pos["x"] ] = 1
  
  return max(sizes)

#return moves in order of which has most space up to size of snake
def dfs_moves(moves:List[dict], grid: List[List[int]], head:tuple) -> List[dict]:
  x=head[0]
  y=head[1]

  count = {
    "up":0,
    "down":0,
    "right":0,
    "left":0
  }
  dumb_count = {
    "up":0,
    "down":0,
    "right":0,
    "left":0
  }

  for m in count:
    if m not in moves:
      continue
    looked = [[0 for x in range(len(grid))] for y in range(len(grid))]
    dumb_looked= [[0 for x in range(len(grid))] for y in range(len(grid))]
    if m=="up":
      #print(f"counting for {m}")
      count[m] = dfs((x+1,y),grid,looked)
      dumb_count[m] = dumb_dfs((x+1,y),grid,dumb_looked,m)
    if m=="down":
      #print(f"counting for {m}")
      count[m] = dfs((x-1,y),grid,looked)
      dumb_count[m] = dumb_dfs((x-1,y),grid,dumb_looked,m)
    if m=="left":
      #print(f"counting for {m}")
      count[m] = dfs((x,y-1),grid,looked)
      dumb_count[m] = dumb_dfs((x,y-1),grid,dumb_looked,m)
    if m=="right":
      #print(f"counting for {m}")
      count[m] = dfs((x,y+1),grid,looked)
      dumb_count[m] = dumb_dfs((x,y+1),grid,dumb_looked,m)

  ret = [dict(sorted(count.items(), key=lambda item: item[1], reverse=True)),dict(sorted(dumb_count.items(), key=lambda item: item[1], reverse=True))]
  return ret

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

def dumb_dfs(p:tuple,grid:List[List[int]],looked:List[List[int]],m:str) ->int:
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
  look_up = 1 if(p[0]+1 < l and looked[p[0]+1][p[1]] == 0) else 0
  look_down = 1 if(p[0]-1 >= 0 and looked[p[0]-1][p[1]] == 0) else 0
  look_right = 1 if (p[1]+1 < l and looked[p[0]][p[1]+1] == 0) else 0
  look_left = 1 if(p[1]-1 >=0 and looked[p[0]][p[1]-1] == 0) else 0
  
  sum = 1
  if m=="up":
    sum += dumb_dfs((p[0]+1,p[1]),grid,looked,m) if look_up else 0
    sum += dumb_dfs((p[0],p[1]+1),grid,looked,m) if look_right else 0
    sum += dumb_dfs((p[0],p[1]-1),grid,looked,m) if look_left else 0  
  elif m=="down":
    sum += dumb_dfs((p[0]-1,p[1]),grid,looked,m) if look_down else 0
    sum += dumb_dfs((p[0],p[1]+1),grid,looked,m) if look_right else 0
    sum += dumb_dfs((p[0],p[1]-1),grid,looked,m) if look_left else 0  
  elif m=="left":
    sum += dumb_dfs((p[0]+1,p[1]),grid,looked,m) if look_up else 0
    sum += dumb_dfs((p[0]-1,p[1]),grid,looked,m) if look_down else 0
    sum += dumb_dfs((p[0],p[1]-1),grid,looked,m) if look_left else 0  
  elif m=="right":
    sum += dumb_dfs((p[0]+1,p[1]),grid,looked,m) if look_up else 0
    sum += dumb_dfs((p[0]-1,p[1]),grid,looked,m) if look_down else 0
    sum += dumb_dfs((p[0],p[1]+1),grid,looked,m) if look_right else 0
  
  return sum

#returns list of legal moves that don't have bad head to head collisions
def head_to_head(moves:List[dict],snakes: List[dict],my_snake:dict) -> List[str]:
#find possible head to head collisions and only remove if the snake is >= 
#check 3x3 space around head
  heads = []
  for s in snakes:
    heads.append(s["body"][0])
  
  print(f"Heads: {heads}")

  #up0, left1, right2, down3, up_left4, up_right5, down_left6, down_right7
  x=my_snake["head"]["x"]
  y=my_snake["head"]["y"]
  checks = [
    {"x":x,"y":y+2},
    {"x":x-2,"y":y},
    {"x":x+2,"y":y},
    {"x":x,"y":y-2},
    {"x":x-1,"y":y+1},
    {"x":x+1,"y":y+1},
    {"x":x-1,"y":y-1},
    {"x":x+1,"y":y-1},
  ]
  hits=[]

  for m in moves:
    if m == "up":
      move_check = [checks[0],checks[4],checks[5]]
    elif m == "left":
      move_check  = [checks[1],checks[4],checks[6]]
    elif m == "right":
      move_check = [checks[2],checks[5],checks[7]]
    elif m == "down":
      move_check = [checks[3],checks[6],checks[7]]

    for s in snakes:
      head=s["body"][0]
      if head in move_check and s["length"]>=my_snake["length"]:
        hits.append(m)
        continue
  
  print(f"Potential head to heads: {hits}")

  return hits

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
def best_move(moves:List[str], dfs:dict, dumb_dfs:dict,head_hits:List[str],food:List[str],me:dict,longest:int)->str:
  #go through bfs and add smallest value of bfs val but move present in moves
  best=[]

  #get best values where they are largest values possible
  for s_m in dfs:
    if s_m in moves:
      if len(best) == 0:
        best.append(s_m)
        continue
      if dfs[best[0]] == dfs[s_m]:  
        best.append(s_m)
          
  print(f"Best moves: {best}")
  #now we have a list of all smallest values
  if(len(best) == 0):
    return "up" #if there are no moves just return up

  best_move = random.choice(best)[0] #default
  if(len(best) == 1):
    return best_move

  #remove head to heads if there are any
  no_head_hits=best
  if(len(head_hits)!=0):
    for h in head_hits:
      if(h in best):
        no_head_hits.remove(h)

    if(len(no_head_hits) != 0):
      best=no_head_hits
      best_move = best[0]

  if(len(best) == 1):
    return best_move
  
  #use worse dfs to determine which direction out of 2 is worse
  if(len(best) == 2):
    if(dumb_dfs[best[0]] > dumb_dfs[best[1]]) and (dumb_dfs[best[1]] <me["length"]*2):
      return best[0]
    elif(dumb_dfs[best[0]] <= dumb_dfs[best[1]]) and (dumb_dfs[best[0]] <me["length"]*2):
      return best[1]
  
  #if for 1+ check if one is in food, return that one
  #only if low or smaller than other snakes
  if(me["health"]<50 or me["length"]<longest):
    for m in best:
      if m in food:
        return m

  return best_move