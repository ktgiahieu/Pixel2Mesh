import os
import pickle

import numpy as np
import torch

from datasets.base_dataset import BaseDataset


class ShapeNet(BaseDataset):
    """
    Dataset wrapping images and target meshes for ShapeNet dataset.
    """

    def __init__(self, file_root, file_list_name, num_points, mesh_pos, normalization):
        super().__init__()
        self.file_root = file_root
        # Read file list
        with open(os.path.join(self.file_root, "meta", file_list_name + ".txt"), "r") as fp:
            self.file_names = fp.read().split("\n")[:-1]
        self.num_points = num_points
        self.normalization = normalization
        self.mesh_pos = mesh_pos

    def __getitem__(self, index):
        label, filename = self.file_names[index].split("_", maxsplit=1)
        with open(os.path.join(self.file_root, "data", label, filename), "rb") as f:
            data = pickle.load(f, encoding="latin1")

        img, pts, normals = data[0].astype(np.float32) / 255.0, data[1][:, :3], data[1][:, 3:]
        pts -= np.array(self.mesh_pos)
        assert pts.shape[0] == normals.shape[0]
        length = pts.shape[0]
        choices = np.resize(np.random.permutation(length), self.num_points)
        pts = pts[choices]
        normals = normals[choices]

        img = torch.from_numpy(np.transpose(img, (2, 0, 1)))
        img_normalized = self.normalize_img(img) if self.normalization else img

        return {
            "images": img_normalized,
            "images_orig": img,
            "points": pts,
            "normals": normals,
            "labels": label,
            "filename": filename,
            "length": length
        }

    def __len__(self):
        return len(self.file_names)
