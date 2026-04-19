from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from recommender import load_data, search_movies, get_recommendations

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

movies = load_data()
P = "https://image.tmdb.org/t/p/w300"

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Pictura</title>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,700;1,500&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#080812;--s1:#0f0f1e;--s2:#161628;--s3:#1e1e35;
  --gold:#f0b429;--gold2:#c8891a;
  --text:#f0f0fa;--t2:#8888aa;--t3:#44445a;
  --border:rgba(255,255,255,0.07);--bordergold:rgba(240,180,41,0.3);
  --r:14px;--rc:18px
}
body{font-family:'Outfit',sans-serif;background:var(--bg);color:var(--text);min-height:100vh}
::-webkit-scrollbar{width:5px}
::-webkit-scrollbar-thumb{background:var(--s3);border-radius:3px}
#collage{position:fixed;inset:0;z-index:0;display:grid;grid-template-columns:repeat(8,1fr);grid-template-rows:repeat(3,1fr);gap:2px;pointer-events:none}
#collage img{width:100%;height:100%;object-fit:cover;opacity:0.28;filter:saturate(0.7)}
#collage-fade{position:fixed;inset:0;z-index:1;background:linear-gradient(to bottom,rgba(8,8,18,0.45) 0%,rgba(8,8,18,0.25) 40%,rgba(8,8,18,0.95) 75%)}
nav{position:relative;z-index:10}
#home,#detail{position:relative;z-index:2}
nav{padding:18px 40px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between}
.logo{font-family:'Playfair Display',serif;font-size:1.5rem;color:var(--gold)}
.logo span{color:var(--text);font-style:italic}
.nav-count{font-size:0.75rem;color:var(--t3)}
.nav-count b{color:var(--t2)}
.hero{padding:70px 24px 48px;text-align:center}
.hero h1{font-family:'Playfair Display',serif;font-size:3.2rem;line-height:1.1;margin-bottom:14px}
.hero h1 em{color:var(--gold);font-style:italic}
.hero p{color:var(--t2);font-size:1rem;font-weight:300;margin-bottom:44px}
.search-wrap{max-width:640px;margin:0 auto;position:relative}
.search-bar{display:flex;align-items:center;background:var(--s1);border:1.5px solid var(--bordergold);border-radius:50px;padding:7px 7px 7px 24px;gap:10px;transition:box-shadow .2s}
.search-bar:focus-within{box-shadow:0 0 0 4px rgba(240,180,41,.1);border-color:var(--gold)}
.search-bar input{flex:1;background:none;border:none;outline:none;color:var(--text);font-size:1rem;font-family:'Outfit',sans-serif}
.search-bar input::placeholder{color:var(--t3)}
.search-bar button{background:var(--gold);border:none;border-radius:40px;padding:11px 30px;color:#080812;font-size:.93rem;font-weight:700;cursor:pointer;font-family:'Outfit',sans-serif;white-space:nowrap}
.search-bar button:hover{background:var(--gold2)}
.sug-box{position:absolute;top:calc(100% + 8px);left:0;right:0;background:var(--s2);border:1px solid var(--bordergold);border-radius:var(--r);overflow:hidden;z-index:50;display:none;box-shadow:0 16px 40px rgba(0,0,0,.5)}
.sug-item{display:flex;align-items:center;gap:12px;padding:11px 16px;cursor:pointer;transition:background .12s}
.sug-item:hover{background:var(--s3)}
.sug-poster{width:34px;height:50px;border-radius:6px;object-fit:cover;background:var(--s3);flex-shrink:0}
.sug-poster-ph{width:34px;height:50px;border-radius:6px;background:var(--s3);flex-shrink:0;display:flex;align-items:center;justify-content:center}
.sug-title{font-size:.88rem;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sug-meta{font-size:.72rem;color:var(--t2);margin-top:2px}
.main{max-width:1160px;margin:0 auto;padding:0 28px 80px}
.shdr{display:flex;align-items:center;gap:12px;margin:36px 0 18px}
.shdr-title{font-size:1rem;font-weight:600;white-space:nowrap}
.shdr-line{flex:1;height:1px;background:var(--border)}
.shdr-sub{font-size:.75rem;color:var(--t3);white-space:nowrap}
.matched-card{display:flex;gap:24px;background:var(--s1);border:1.5px solid var(--bordergold);border-radius:var(--rc);padding:24px;margin-bottom:8px;cursor:pointer;transition:border-color .2s}
.matched-card:hover{border-color:var(--gold);box-shadow:0 8px 32px rgba(240,180,41,.08)}
.mc-poster{width:120px;min-width:120px;height:180px;border-radius:10px;object-fit:cover;background:var(--s2)}
.mc-poster-ph{width:120px;min-width:120px;height:180px;border-radius:10px;background:var(--s2);display:flex;align-items:center;justify-content:center;font-size:3rem}
.mc-body{flex:1;min-width:0}
.mc-eyebrow{font-size:.68rem;letter-spacing:2px;text-transform:uppercase;color:var(--gold);margin-bottom:8px}
.mc-title{font-family:'Playfair Display',serif;font-size:1.8rem;margin-bottom:10px;line-height:1.2}
.mc-genres{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px}
.mc-genre{padding:3px 12px;border-radius:20px;background:rgba(155,127,232,.12);border:1px solid rgba(155,127,232,.25);color:#b8a8f0;font-size:.72rem;font-weight:500}
.mc-overview{font-size:.85rem;color:var(--t2);line-height:1.7;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;margin-bottom:14px}
.mc-rating{display:flex;align-items:center;gap:8px}
.mc-star{font-size:1rem;font-weight:700;color:var(--gold)}
.mc-hint{font-size:.72rem;color:var(--t3);margin-left:auto}
.mgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(155px,1fr));gap:16px}
.mtile{cursor:pointer;border-radius:var(--r);overflow:hidden;background:var(--s1);border:1px solid var(--border);transition:transform .2s,border-color .2s}
.mtile:hover{transform:translateY(-5px);border-color:var(--bordergold)}
.mtile-img{width:100%;aspect-ratio:2/3;object-fit:cover;background:var(--s2);display:block}
.mtile-img-ph{width:100%;aspect-ratio:2/3;background:var(--s2);display:flex;align-items:center;justify-content:center;font-size:2.2rem}
.mtile-body{padding:10px 12px}
.mtile-title{font-size:.78rem;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-bottom:3px}
.mtile-rating{font-size:.72rem;color:var(--gold)}
#detail{display:none}
.back-btn{display:inline-flex;align-items:center;gap:7px;background:var(--s1);border:1px solid var(--border);border-radius:30px;padding:9px 20px;color:var(--t2);font-size:.82rem;cursor:pointer;margin-bottom:28px;font-family:'Outfit',sans-serif;transition:all .15s}
.back-btn:hover{border-color:var(--gold);color:var(--gold)}
.detail-hero{display:flex;gap:32px;margin-bottom:36px}
.dp-poster{width:200px;min-width:200px;height:300px;border-radius:14px;object-fit:cover;background:var(--s2)}
.dp-poster-ph{width:200px;min-width:200px;height:300px;border-radius:14px;background:var(--s2);display:flex;align-items:center;justify-content:center;font-size:4rem}
.dp-title{font-family:'Playfair Display',serif;font-size:2.2rem;margin-bottom:12px;line-height:1.2}
.dp-genres{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:16px}
.dp-genre{padding:4px 14px;border-radius:20px;background:rgba(155,127,232,.12);border:1px solid rgba(155,127,232,.25);color:#b8a8f0;font-size:.75rem}
.dp-rating{font-size:2rem;font-weight:700;color:var(--gold);margin-bottom:16px}
.dp-overview{font-size:.9rem;color:var(--t2);line-height:1.8}
.spinner-wrap{text-align:center;padding:60px}
.spinner{width:36px;height:36px;border:3px solid var(--s3);border-top-color:var(--gold);border-radius:50%;animation:spin .7s linear infinite;margin:0 auto}
@keyframes spin{to{transform:rotate(360deg)}}
.empty{text-align:center;padding:80px;color:var(--t3);font-size:.9rem}
.errbx{background:rgba(200,50,50,.08);border:1px solid rgba(200,50,50,.2);border-radius:var(--r);padding:16px 20px;color:#f09090;font-size:.88rem}
@media(max-width:600px){
  .hero h1{font-size:2.1rem}.matched-card{flex-direction:column}
  .mc-poster,.mc-poster-ph{width:100%;height:220px;min-width:unset}
  .detail-hero{flex-direction:column}.dp-poster,.dp-poster-ph{width:100%;height:260px;min-width:unset}
  nav{padding:14px 20px}.main{padding:0 16px 60px}
}
</style>
</head>
<body>
<div id="collage"></div>
<div id="collage-fade"></div>
<nav>
  <div class="logo">Pictu<span>ra</span></div>
  <div class="nav-count">Search across <b>50,381</b> movies</div>
</nav>

<div id="home">
  <div class="hero">
    <h1>Find your next<br><em>great film</em></h1>
    <p>50,000+ movies &bull; instant search &bull; smart recommendations</p>
    <div class="search-wrap">
      <div class="search-bar">
        <input id="q" type="text" placeholder="Search any movie... Batman, Spider-Man, Inception" autocomplete="off">
        <button onclick="doSearch()">Search</button>
      </div>
      <div class="sug-box" id="sugbox"></div>
    </div>
  </div>
  <div class="main" id="results"><div class="empty">Search a movie to get started</div></div>
</div>

<div id="detail">
  <div class="main" style="padding-top:32px">
    <button class="back-btn" onclick="goBack()">&#8592; Back</button>
    <div id="detail-body"></div>
  </div>
</div>

<script>
var P="https://image.tmdb.org/t/p/w300";
var sugTimer=null;

async function buildCollage(){
  try{
    var r=await fetch('/posters');
    var d=await r.json();
    var c=document.getElementById('collage');
    d.posters.forEach(function(p){
      var img=document.createElement('img');
      img.src=P+p;img.alt='';img.loading='lazy';
      c.appendChild(img);
    });
  }catch(e){}
}
buildCollage();

document.getElementById('q').addEventListener('input',function(){
  clearTimeout(sugTimer);
  var q=this.value.trim();
  if(q.length<2){hideSug();return;}
  sugTimer=setTimeout(function(){loadSug(q);},280);
});

async function loadSug(q){
  try{
    var r=await fetch('/suggest?q='+encodeURIComponent(q));
    var d=await r.json();
    if(!d.results.length){hideSug();return;}
    var box=document.getElementById('sugbox');
    box.innerHTML=d.results.map(function(m){
      var img=m.poster_path?'<img class="sug-poster" src="'+P+m.poster_path+'">':'<div class="sug-poster-ph">&#127916;</div>';
      var g=(m.genres||'').split('|').slice(0,2).join(' · ');
      return '<div class="sug-item" onclick="openDetail('+m.movieId+')">'+img+
        '<div><div class="sug-title">'+esc(m.title)+'</div>'+
        '<div class="sug-meta">'+g+(m.vote_average?' &bull; &#9733; '+m.vote_average.toFixed(1):'')+'</div></div></div>';
    }).join('');
    box.style.display='block';
  }catch(e){hideSug();}
}

function hideSug(){document.getElementById('sugbox').style.display='none';}
document.addEventListener('click',function(e){if(!e.target.closest('.search-wrap'))hideSug();});
document.getElementById('q').addEventListener('keydown',function(e){if(e.key==='Enter')doSearch();});

async function doSearch(){
  var q=document.getElementById('q').value.trim();
  if(!q)return;
  hideSug();
  var div=document.getElementById('results');
  div.innerHTML='<div class="spinner-wrap"><div class="spinner"></div></div>';
  try{
    var r=await fetch('/search?q='+encodeURIComponent(q));
    var d=await r.json();
    if(!r.ok){div.innerHTML='<div class="errbx">'+d.detail+'</div>';return;}
    renderResults(d);
  }catch(e){div.innerHTML='<div class="errbx">Something went wrong. Please try again.</div>';}
}

function renderResults(d){
  var div=document.getElementById('results');
  var m=d.matched;
  var poster=m.poster_path?'<img class="mc-poster" src="'+P+m.poster_path+'">':'<div class="mc-poster-ph">&#127916;</div>';
  var genres=(m.genres||'').split('|').map(function(g){return '<span class="mc-genre">'+esc(g)+'</span>';}).join('');
  var html='<div class="matched-card" onclick="openDetail('+m.movieId+')" title="Click for details">'+
    poster+'<div class="mc-body">'+
    '<div class="mc-eyebrow">&#10003; Best match</div>'+
    '<div class="mc-title">'+esc(m.title)+'</div>'+
    '<div class="mc-genres">'+genres+'</div>'+
    '<div class="mc-overview">'+(m.overview||'No description available.')+'</div>'+
    '<div class="mc-rating"><div class="mc-star">&#9733; '+(m.vote_average?m.vote_average.toFixed(1):'N/A')+' / 10</div>'+
    '<div class="mc-hint">Click for details &#8594;</div></div>'+
    '</div></div>';
  if(d.others&&d.others.length){html+=shdr('Other matches',d.others.length+' results');html+='<div class="mgrid">'+d.others.map(tile).join('')+'</div>';}
  if(d.recs&&d.recs.length){html+=shdr('Recommended',d.recs.length+' picks based on '+esc(m.title));html+='<div class="mgrid">'+d.recs.map(tile).join('')+'</div>';}
  div.innerHTML=html;
}

async function openDetail(id){
  document.getElementById('home').style.display='none';
  document.getElementById('detail').style.display='block';
  window.scrollTo(0,0);
  var db=document.getElementById('detail-body');
  db.innerHTML='<div class="spinner-wrap"><div class="spinner"></div></div>';
  try{
    var r=await fetch('/movie/'+id);
    var d=await r.json();
    if(!r.ok){db.innerHTML='<div class="errbx">'+d.detail+'</div>';return;}
    var poster=d.poster_path?'<img class="dp-poster" src="'+P+d.poster_path+'">':'<div class="dp-poster-ph">&#127916;</div>';
    var genres=(d.genres||'').split('|').map(function(g){return '<span class="dp-genre">'+esc(g)+'</span>';}).join('');
    var html='<div class="detail-hero">'+poster+'<div>'+
      '<div class="dp-title">'+esc(d.title)+'</div>'+
      '<div class="dp-genres">'+genres+'</div>'+
      '<div class="dp-rating">&#9733; '+(d.vote_average?d.vote_average.toFixed(1):'N/A')+' / 10</div>'+
      '<div class="dp-overview">'+(d.overview||'No description available.')+'</div>'+
      '</div></div>';
    if(d.recs&&d.recs.length){html+=shdr('More like this',d.recs.length+' picks');html+='<div class="mgrid">'+d.recs.map(tile).join('')+'</div>';}
    db.innerHTML=html;
  }catch(e){db.innerHTML='<div class="errbx">Failed to load.</div>';}
}

function goBack(){document.getElementById('detail').style.display='none';document.getElementById('home').style.display='block';window.scrollTo(0,0);}

function tile(m){
  var img=m.poster_path?'<img class="mtile-img" src="'+P+m.poster_path+'" loading="lazy">':'<div class="mtile-img-ph">&#127916;</div>';
  return '<div class="mtile" onclick="openDetail('+m.movieId+')">'+img+
    '<div class="mtile-body"><div class="mtile-title">'+esc(m.title)+'</div>'+
    '<div class="mtile-rating">&#9733; '+(m.vote_average?m.vote_average.toFixed(1):'?')+'</div></div></div>';
}

function shdr(t,s){return '<div class="shdr"><div class="shdr-title">'+t+'</div><div class="shdr-line"></div><div class="shdr-sub">'+s+'</div></div>';}
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
</script>
</body>
</html>"""


def to_dict(row):
    d = row.to_dict() if hasattr(row, 'to_dict') else dict(row)
    d["movieId"]      = int(d.get("movieId", 0))
    d["vote_average"] = round(float(d.get("vote_average", 0)), 1)
    d["poster_path"]  = str(d.get("poster_path", "") or "").strip()
    d["overview"]     = str(d.get("overview", "") or "")
    d["genres"]       = str(d.get("genres", "") or "")
    d["title"]        = str(d.get("title", ""))
    return d

def df_to_list(df):
    return [to_dict(r) for _, r in df.iterrows()]


@app.get("/", response_class=HTMLResponse)
def home():
    return HTML

@app.get("/posters")
def posters():
    # Pull top popular movies that have a poster, for the background collage
    sample = movies[movies["poster_path"].str.len() > 3].sort_values("popularity", ascending=False).head(200)
    # Shuffle so it looks different each refresh
    shuffled = sample.sample(frac=1, random_state=42).head(24)
    return {"posters": shuffled["poster_path"].tolist()}

@app.get("/suggest")
def suggest(q: str = Query(..., min_length=2)):
    r = search_movies(q, movies, limit=6)
    return {"results": df_to_list(r) if not r.empty else []}

@app.get("/search")
def search(q: str = Query(...)):
    r = search_movies(q, movies, limit=10)
    if r.empty:
        raise HTTPException(404, detail=f"No movies found matching '{q}'.")
    matched = to_dict(r.iloc[0])
    others  = df_to_list(r.iloc[1:6]) if len(r) > 1 else []
    try:
        recs = df_to_list(get_recommendations(matched["movieId"], movies, n=12))
    except Exception:
        recs = []
    return {"matched": matched, "others": others, "recs": recs}

@app.get("/movie/{movie_id}")
def movie_detail(movie_id: int):
    row = movies[movies["movieId"] == movie_id]
    if row.empty:
        raise HTTPException(404, detail="Movie not found.")
    details = to_dict(row.iloc[0])
    try:
        recs = df_to_list(get_recommendations(movie_id, movies, n=12))
    except Exception:
        recs = []
    details["recs"] = recs
    return details
