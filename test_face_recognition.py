#!/usr/bin/python
#-*-coding:utf-8-*-


import face_recognition
from PIL import Image

known_faces = []
known_face_names = []
def add_data(list):
    '''数据格式[{'name':'pic_name','pic':'pic_path'},....]'''
    try:
        for pople_dic in list:
            name = pople_dic['name']
            pic_file =  pople_dic['pic']
            known_faces.append( face_recognition.face_encodings(face_recognition.load_image_file(pic_file))[0])
            known_face_names.append(name)
    except IndexError:
        print("I wasn't able to locate any faces in at least one of the images. Check the image files. Aborting...")
        quit()

def compareFaces(pic_file):
    try:
        unknown_image = face_recognition.load_image_file(pic_file)
        unknown_face_locations = face_recognition.face_locations(unknown_image)
        unknown_face_encodings = face_recognition.face_encodings(unknown_face_locations)
    except IndexError:
        print("I wasn't able to locate any faces in at least one of the images. Check the image files. Aborting...")
        quit()
    count = 0
    for unknown_face_encoding in unknown_face_encodings:
        count +=1
        results = face_recognition.compare_faces(known_faces, unknown_face_encoding)
        index =0
        flag = True
        for result in results:
            if result:
                flag = False
                print "NO.%d Is the unknown face a picture of %s? {}".format(results[1]) %(count,known_face_names[index])
                top, right, bottom, left = unknown_face_locations[count]
                face_image = unknown_image[top:bottom, left:right]
                pil_image = Image.fromarray(face_image)
                pil_image.save("new_pic/%s-NO.%d.jpg" % (known_face_names[index],count))
                break
            index += 1
        if flag:
            print "NO.%d Is the unknown face a new person that we've never seen before? {}".format(not True in results) %count


if __name__ == '__main__':
    data = [{'name':'biden','pic':'pic/biden.jpg'},{'name':'obama','pic':'pic/obama.jpg'}]
    add_data(data)
    pic_file = "pic/many.jpg"
    compareFaces(pic_file)