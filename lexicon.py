import _mysql
import json
db=_mysql.connect("localhost","root","","lexicon_hebrew")
stat_file = open("stats_quirk.json")
stats = json.load(stat_file)
book_file = open("books.json")
books = json.load(book_file)

def dump_book(name, bno):

  interlinear = []

  # get num chapters
  nchapters = int(len(stats[bno].keys()))
  print (name, nchapters)

  # iterate over each chapter of the book
  for i in xrange(1,nchapters+1):
   cno = str(i)
   nverses = int(stats[bno][cno])+1
   for j in xrange(1,nverses):
    vno = str(j)
    db.query("""select strongs from bible_original where book={} and chapter={} and verse={}""".format(bno, cno, vno))
    r=db.use_result()

    words = []
    doc_id = "{}{}{}".format(bno.zfill(2), cno.zfill(3), vno.zfill(3))

    # load json chapter
    path="src/"+name+"/"
    filename = path+cno+".json"
    i = 0
    with open(filename) as data_file:

        # get the unordered json verse
        uverse = json.load(data_file)[vno]
        while True:
          val = r.fetch_row()
          if len(val) == 0:
             break

          # get strongs num
          strongs_prefix = 'h'
          if int(bno) >= 40:
              strongs_prefix = 'g'
          strongs = strongs_prefix+val[0][0]

          # lookup interlinear text
          match = [v for v in uverse if v['number'] == strongs]

          # append word
          doc = None 
          if len(match) > 0:
             doc = match[0]
          else:
             doc = {"text": "", "number": strongs}
          doc["i"] = i
          words.append(doc)
          i += 1

    # append verse
    interlinear.append({"id": doc_id, "verse": words})
  return interlinear

def filter_func(char):
    return char == '\n' or 32 <= ord(char) <= 126

if __name__ == "__main__":

    db.query("""select *  from lexicon_hebrew""")
    r=db.use_result()

    # id, strongs, base_word, data, usage
    lexicon = []
    while True:
        row = r.fetch_row()
        if len(row) == 0:
            break
        val = row[0]
        _id = val[0] 
        strongs = "h"+val[1] 
        base_word = val[2] 
        usage = filter(filter_func, val[4]).lower()
        filtered_data = filter(filter_func, val[3]).lower()
        data = json.loads(filtered_data)
        del data["pronun"]
        doc = {"strongs": strongs,
               "word": usage,
               "data": data}
        lexicon.append(doc)
   
    output = open("lexicon/hebrew.json", "w")
    jsdata = json.dumps(lexicon)
    output.write(jsdata)
