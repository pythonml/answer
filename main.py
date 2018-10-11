import argparse
import time
import json
import requests
import pymongo

def get_answers_by_page(topic_id, page_no):
    offset = page_no * 10
    url = "https://www.zhihu.com/api/v4/topics/" + str(topic_id) + "/feeds/essence?include=data%5B%3F(target.type%3Dtopic_sticky_module)%5D.target.data%5B%3F(target.type%3Danswer)%5D.target.content%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%3F(target.type%3Dtopic_sticky_module)%5D.target.data%5B%3F(target.type%3Danswer)%5D.target.is_normal%2Ccomment_count%2Cvoteup_count%2Ccontent%2Crelevant_info%2Cexcerpt.author.badge%5B%3F(type%3Dbest_answerer)%5D.topics%3Bdata%5B%3F(target.type%3Dtopic_sticky_module)%5D.target.data%5B%3F(target.type%3Darticle)%5D.target.content%2Cvoteup_count%2Ccomment_count%2Cvoting%2Cauthor.badge%5B%3F(type%3Dbest_answerer)%5D.topics%3Bdata%5B%3F(target.type%3Dtopic_sticky_module)%5D.target.data%5B%3F(target.type%3Dpeople)%5D.target.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics%3Bdata%5B%3F(target.type%3Danswer)%5D.target.annotation_detail%2Ccontent%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%3F(target.type%3Danswer)%5D.target.author.badge%5B%3F(type%3Dbest_answerer)%5D.topics%3Bdata%5B%3F(target.type%3Darticle)%5D.target.annotation_detail%2Ccontent%2Cauthor.badge%5B%3F(type%3Dbest_answerer)%5D.topics%3Bdata%5B%3F(target.type%3Dquestion)%5D.target.annotation_detail%2Ccomment_count&limit=10&offset=" + str(page_no)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
    }
    r = requests.get(url, verify=False, headers=headers)
    content = r.content.decode("utf-8")
    data = json.loads(content)
    is_end = data["paging"]["is_end"]
    items = data["data"]
    client = pymongo.MongoClient()
    db = client["zhihu"]
    if len(items) > 0:
        db.answers.insert_many(items)
        db.saved_topics.insert({"topic_id": topic_id, "page_no": page_no})
    return is_end

def get_answers(topic_id):
    page_no = 0
    client = pymongo.MongoClient()
    db = client["zhihu"]
    while True:
        is_saved = db.saved_topics.find({"topic_id": topic_id, "page_no": page_no}).count()
        if is_saved:
            print("{} {} already saved".format(topic_id, page_no))
            page_no += 1
            continue
        print(topic_id, page_no)
        is_end = get_answers_by_page(topic_id, page_no)
        page_no += 1
        if is_end:
            break

def query():
    client = pymongo.MongoClient()
    db = client["zhihu"]
    items = db.answers.aggregate([
        {"$addFields": {"answer_len": {"$strLenCP": "$target.content"}}},
        {"$match": {"answer_len": {"$lte": 50}}},
    ])
    answer_ids = []
    for item in items:
        item_type = item["target"]["type"]
        if item_type != "answer":
            continue
        question = item["target"]["question"]["title"]
        answer = item["target"]["content"]
        vote_num = item["target"]["voteup_count"]
        if vote_num < 1000:
            continue
        answer_id = item["target"]["id"]
        if answer_id in answer_ids:
            continue
        url = item["target"]["url"]
        print("=" * 50)
        print("Q: {}\nA: {}\nvote: {}".format(question, answer, vote_num))
        answer_ids.append(answer_id)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--save", help="save data", action="store_true", dest="save")
    parser.add_argument("--query", help="query data", action="store_true", dest="query")
    args = parser.parse_args()

    if args.save:
        topic_ids = [19554298, 19552330, 19565652, 19580349, 19939299, 19555547, 19594551, 19552832, 19577377, 19552826, 19615452]
        for topic_id in topic_ids:
            get_answers(topic_id)
    elif args.query:
        query()
