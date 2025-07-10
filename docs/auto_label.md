# Auto label methods



## Message queue's message format

```
Topic: predict.${type}.${method}
```

- Predict single image by yolo
    - Topic: `predict.image.yolo`
- Predict whole dataeset by yolo
    - Topic: `predict.dataset.image`



----

## Auto label per dataset

- [YOLO-world model](https://docs.ultralytics.com/models/yolo-world/)
- Define custom classes or using COCO


## Auto label per image

- [YOLO-world model](https://docs.ultralytics.com/models/yolo-world/)