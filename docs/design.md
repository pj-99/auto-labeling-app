# Deisgn

## Feature Requirements
    1. Create dataset
	2. Upload images to dataset
	3. Auto labeling => Can choose different method
	4. Export dataset?

---

## APIs

Core:
- [x] created dateset
- [x] add image to dataset
	- 1. `generate_signed_url()`
	- 2. Use signed url to upload image, get image url
	- 2. `insert_image_to_dataset(image_url, ...)`
- [ ] update dataset classes
	- 1. insert_class(dataset_id), delete_class(dataset_id, class_id)
	- 2. rename_class(dataeset_id, class_id)
- [ ] label an image
	- 1. query labels(image, dataset_id) => A bounch of bounding boxes and class
	- 2. update_lables(image_id, dataset_id)
	- [ ] detection
	- [ ] segmentatoin
- [ ] support auto label by models

Todo:
- Dataset training type?

Additional:
- auth