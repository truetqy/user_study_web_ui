from flask import Flask, render_template, url_for, request, redirect
import os, os.path
import json
app = Flask(__name__)
dataset = json.load(open('coco_caption_QAE.json'))
img_ids = dataset['img_ids']
img_id2QAs = dataset['img_id2QAs']
img_id2captions = dataset['img_id2captions']
img_id2split = dataset['img_id2split']
server_ip = 'http://172.21.1.1:5000'
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/redirect_user')
def redirect_user():
    for uid in range(0,20):
        user_result_dir = './users/u%d/result/'%uid
        if len(os.listdir(user_result_dir))==0 and not os.path.exists('./users/u%d/on_hold.json'%(uid)):
            with open('./users/u%d/on_hold.json'%(uid), 'w') as outfile:
                json.dump([1], outfile)
            return redirect('%s/%d'%(server_ip,uid))
    return redirect('%s/thanks'%server_ip)

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')


@app.route('/<int:uid>', methods=['GET', 'POST'])

# @app.route('/post/<int:post_id>')
# def show_post(post_id):
#     # show the post with the given id, the id is an integer
#     return 'Post %d' % post_id
def start(uid):
    # if not os.path.exists('./users/u%d/on_hold.json'%(uid)):
    #     with open('./users/u%d/on_hold.json'%(uid), 'w') as outfile:
    #         json.dump([1], outfile)
    im_q_list = json.load(open('./users/u%d/im_q_list.json'%(uid)))
    if request.method == 'POST':
        print 'saving --- '
        fluent = request.form['fluent']
        correct = request.form['correct']
        relevant= request.form['relevant']
        complementary = request.form['complementary']
        imid = request.form['imid']
        qid = request.form['qid']
        question_type = request.form['question_type']
        print '<%s,%s,%s>'%(imid,qid,question_type)
        result = {'imid':int(imid),'qid':int(qid),'fluent_score':int(fluent),'correct_score':int(correct),
        'relevant_score':int(relevant),'complementary_score':int(complementary),'question_type':question_type}
        with open('./users/u%d/result/%d_%d.json'%(uid,int(imid),int(qid)), 'w') as outfile:
            json.dump(result, outfile)

        print request.form

    user_result_dir = './users/u%d/result/'%uid
    postid = len(os.listdir(user_result_dir))
    if postid==len(im_q_list):
        return redirect('%s/thanks'%server_ip)
    print 'loading --- '
    imid =im_q_list[postid][0]
    qid = im_q_list[postid][1]
    img_folder = 'static/cocodata'
    split = img_id2split[str(img_ids[imid])]
    imfile  = r'%s/%s2014/COCO_%s2014_%012d.jpg'%(img_folder, split, split, int(img_ids[imid]))
    qae = img_id2QAs[str(img_ids[imid])][qid]
    question = qae['question']
    question_type = qae['question_type']
    print '<%s,%s,%s>'%(imid,qid,question_type)
    answer = qae['multiple_choice_answer']
    explanation = str(qae['explanation'][0])
    print 'uid--', uid
    prog = int(float(postid)/len(im_q_list)*100)
    print 'prog--',prog
    return render_template('start.html',imfile=imfile, question=question,
    answer=answer,explanation=explanation,imid=imid,qid=qid,postid=postid,question_type=question_type,prog=prog)
