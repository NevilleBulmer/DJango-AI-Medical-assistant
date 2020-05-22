from VGG_classification import VGG_classification as VGGCla

from InputFile import inpuCreate as inpInit
import easygui
import cv2

path1 = easygui.fileopenbox()
iputImg = cv2.imread(path1)
cv2.imshow('Input image ', iputImg)
cv2.waitKey(0)
cv2.destroyAllWindows()
inpInit.InputMain()
SegmentImg = ResSeg.PredictionTrainTest(8, iputImg)
cv2.imshow('Segmented image', SegmentImg)
cv2.waitKey(0)
cv2.destroyAllWindows()
Resultclass = VGGCla.PredictVGG(SegmentImg, path1)
if Resultclass == 0:
    print('High Grade Tumor')
elif Resultclass == 1:
    print('Low Grade Tumor')
else:
    print('Image not valid')
