import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import VGG16
from tensorflow.keras.layers import Dense, Flatten, Dropout
from tensorflow.keras.models import Model
import json
import os

dataset_dir = "dataset"   # ✅ इथे "rice_dataset" ऐवजी "dataset" कर

img_size = (224,224)
batch_size = 32

datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2
)
train_data = datagen.flow_from_directory(
    dataset_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode="categorical",
    subset="training"
)
val_data = datagen.flow_from_directory(
    dataset_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode="categorical",
    subset="validation"
)
base_model = VGG16(
    weights="imagenet",
    include_top=False,
    input_shape=(224,224,3)
)
for layer in base_model.layers:
    layer.trainable = False

x = base_model.output
x = Flatten()(x)
x = Dense(256,activation="relu")(x)
x = Dropout(0.5)(x)

predictions = Dense(train_data.num_classes,activation="softmax")(x)

model = Model(inputs=base_model.input,outputs=predictions)

model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)
model.fit(
    train_data,
    validation_data=val_data,
    epochs=15   # ✅ 10 ठेव किंवा 20 करू शकतो
)
os.makedirs("ml_model",exist_ok=True)
model.save("ml_model/crop_disease_model.h5")

with open("ml_model/class_indices.json","w") as f:
    json.dump(train_data.class_indices,f)
print("Model Training Complete")