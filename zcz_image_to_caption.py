import pickle
import torch
from detectron2.checkpoint import DetectionCheckpointer
from detectron2.config import get_cfg
from detectron2.engine import DefaultTrainer
from bottom_up_attention.utils.extract_utils import get_image_blob
from bottom_up_attention.bua.caffe.modeling.layers.nms import nms
from bottom_up_attention.bua.d2 import add_attribute_config
import sys
sys.path.insert(0,'meshed_memory_transformer')
from data import TextField
from models.transformer import Transformer, MemoryAugmentedEncoder, MeshedDecoder, ScaledDotProductAttentionMemory

# 从数据库读取模型
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

secret_id = 'AKID86oGSwA7oENFqBG4cttcASTDgS1JL6bp' 
secret_key = 'yf6HCpCIAm9F6h4C3e18yYruiIdkcFcj'   
region = 'ap-shanghai'      
token = None               
scheme = 'https'
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
client = CosS3Client(config)
response = client.get_object(
    Bucket='7072-prod-1gxq0vrt5f11b56e-1310101813',
    Key='cloud://prod-1gxq0vrt5f11b56e.7072-prod-1gxq0vrt5f11b56e-1310101813/models/bua-d2-frcn-r101.pth'
)
response['Body'].get_stream_to_file('bottom_up_attention/bua-d2-frcn-r101.pth')
response = client.get_object(
    Bucket='7072-prod-1gxq0vrt5f11b56e-1310101813',
    Key='cloud://prod-1gxq0vrt5f11b56e.7072-prod-1gxq0vrt5f11b56e-1310101813/models/meshed_memory_transformer.pth'
)
response['Body'].get_stream_to_file('meshed_memory_transformer/meshed_memory_transformer.pth')



config_file = 'bottom_up_attention/configs/d2/test-d2-r101.yaml'
mode = "d2"
cfg = get_cfg()
cfg.defrost()
add_attribute_config(cfg)
cfg.merge_from_file(config_file)
cfg.merge_from_list(['MODEL.BUA.EXTRACT_FEATS',True])
cfg.freeze()

MIN_BOXES = 10
MAX_BOXES = 20
CONF_THRESH = 0.4
model1 = DefaultTrainer.build_model(cfg)
DetectionCheckpointer(model1, save_dir=cfg.OUTPUT_DIR).resume_or_load(
    'bottom_up_attention/'+cfg.MODEL.WEIGHTS, resume=True
)
model1.eval()

def model_inference(model1, batched_inputs, mode):
    if mode == "caffe":
        return model1(batched_inputs)
    elif mode == "d2":
        images = model1.preprocess_image(batched_inputs)
        features = model1.backbone(images.tensor)
        if model1.proposal_generator:
            proposals, _ = model1.proposal_generator(images, features, None)
        else:
            assert "proposals" in batched_inputs[0]
            proposals = [x["proposals"].to(model1.device) for x in batched_inputs]
        return model1.roi_heads(images, features, proposals, None)
    else:
        raise Exception("detection model not supported: {}".format(mode))






# 定义模型  文本生成模型
text_field = TextField(init_token='<bos>', eos_token='<eos>', lower=True, tokenize='spacy',
                           remove_punctuation=True, nopoints=False)
text_field.vocab = pickle.load(open('meshed_memory_transformer/vocab.pkl', 'rb'))
encoder = MemoryAugmentedEncoder(3, 0, attention_module=ScaledDotProductAttentionMemory,
                                     attention_module_kwargs={'m': 40})
decoder = MeshedDecoder(len(text_field.vocab), 54, 3, text_field.vocab.stoi['<pad>'])
device = torch.device('cpu')
model2 = Transformer(text_field.vocab.stoi['<bos>'], encoder, decoder).to(device)

# 导入模型参数
data = torch.load('meshed_memory_transformer/meshed_memory_transformer.pth',map_location=torch.device('cpu'))
model2.load_state_dict(data['state_dict'])

# 测试模型
model2.eval()



def image_to_caption(image):
    dataset_dict = get_image_blob(image, cfg.MODEL.PIXEL_MEAN)
    with torch.set_grad_enabled(False):
        boxes, scores, features_pooled, attr_scores = model_inference(model1,[dataset_dict],mode)
    dets = boxes[0].tensor.cpu() / dataset_dict['im_scale']
    scores = scores[0].cpu()
    feats = features_pooled[0].cpu()
    attr_scores = attr_scores[0].cpu()
    max_conf = torch.zeros((scores.shape[0])).to(scores.device)
    for cls_ind in range(1, scores.shape[1]):
            cls_scores = scores[:, cls_ind]
            keep = nms(dets, cls_scores, 0.3)
            max_conf[keep] = torch.where(cls_scores[keep] > max_conf[keep],
                                        cls_scores[keep],
                                        max_conf[keep])
    keep_boxes = torch.nonzero(max_conf >= CONF_THRESH).flatten()
    if len(keep_boxes) < MIN_BOXES:
        keep_boxes = torch.argsort(max_conf, descending=True)[:MIN_BOXES]
    elif len(keep_boxes) > MAX_BOXES:
        keep_boxes = torch.argsort(max_conf, descending=True)[:MAX_BOXES]
    features = feats[keep_boxes]
    features = features.unsqueeze(0)

    features = features.to(device)
    out, _ = model2.beam_search(features, 20, text_field.vocab.stoi['<eos>'], 5, out_size=1)
    caps_gen = text_field.decode(out, join_words=False)

    res = []
    for i in range(len(caps_gen)):
        res.append(" ".join(caps_gen[i]))
    return res[0]