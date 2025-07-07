# Deisgn

## Feature Requirements
    1. Create dataset
	2. Upload images to dataset
	3. Auto labeling => Can choose different method
	4. Export dataset?

---

## Features and APIs

Core:
- [x] created dateset
- [x] add image to dataset
	- 1. `generate_signed_url()`
	- 2. Use signed url to upload image, get image url
	- 2. `insert_image_to_dataset(image_url, ...)`
- [x] update dataset classes
	- 1. insert_class(dataset_id), delete_class(dataset_id, class_id)
- [x] label an image
	- 1. query labels(image, dataset_id) => A bunch of bounding boxes and class
	- 2. update_labels(image_id, dataset_id)
	- [x] detection
	- [x] segmentation
	- decide training type in dataset level
- [x] support auto label by models	
	- detection
		- [x] SAM: point-prompt  -> bbox
	- segmentation
		- [x] SAM: point-pormpt -> mask
	- [ ] grounding dino or YOLO
----


### 🧩 Frontend TODO

- [ ] Refactor `detect.vue` and `segment.vue`: API calls are triggered multiple times unexpectedly, causing duplicate requests.

- [ ] Fix label rendering issues*: Occasionally, labels fail to render

- [ ] Handle nested labels more robustly: Drawing one label inside another causes unexpected behavior or bugs.

- [ ] Improve SAM-generated segmentation usability: Generated masks contain too many points, making them difficult for users to edit.


Todo or Think:
- Traversal between image -> pagination

Additional:
- auth
- grpahql error handling
- refactor the test using lib for simplify