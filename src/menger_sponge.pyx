import numpy as np
cimport numpy as np
from cython cimport boundscheck, wraparound

@boundscheck(False)
@wraparound(False)
def generate_menger_sponge(int iterations):
    cdef list vertices = []
    cdef list vertex_normals = []

    # Call the recursive function
    recurse(iterations, 0.0, 0.0, 0.0, 1.0, vertices, vertex_normals)

    # Convert lists to NumPy arrays and return
    return np.array(vertices, dtype=np.float32), np.array(vertex_normals, dtype=np.float32)


# Recursive helper function
cdef void recurse(int level, float x, float y, float z, float size, list vertices, list vertex_normals):
    # All variables must be declared at the start
    cdef float half, new_size
    cdef int dx, dy, dz, i, j
    cdef int[:, :] faces
    cdef float[:, :] offsets
    cdef float[:, :] face_normals
    cdef int[:] face
    cdef float[3] vertex
    cdef list temp_list

    if level == 0:
        half = size / 2.0
        offsets = np.array([
            [x - half, y - half, z - half],
            [x + half, y - half, z - half],
            [x + half, y + half, z - half],
            [x - half, y + half, z - half],
            [x - half, y - half, z + half],
            [x + half, y - half, z + half],
            [x + half, y + half, z + half],
            [x - half, y + half, z + half]
        ], dtype=np.float32)

        faces = np.array([
            [0, 1, 2], [2, 3, 0],  # Front face
            [4, 5, 6], [6, 7, 4],  # Back face
            [0, 1, 5], [5, 4, 0],  # Bottom face
            [2, 3, 7], [7, 6, 2],  # Top face
            [1, 2, 6], [6, 5, 1],  # Right face
            [0, 3, 7], [7, 4, 0]   # Left face
        ], dtype=np.int32)

        face_normals = np.array([
            [0, 0, -1], [0, 0, -1],
            [0, 0, 1], [0, 0, 1],
            [0, -1, 0], [0, -1, 0],
            [0, 1, 0], [0, 1, 0],
            [1, 0, 0], [1, 0, 0],
            [-1, 0, 0], [-1, 0, 0]
        ], dtype=np.float32)

        # Manually iterate through faces and append corresponding vertices
        for i in range(faces.shape[0]):
            face = faces[i]
            for j in range(3):
                idx = face[j]
                # Convert the memoryview slice to a Python list
                vertex = [offsets[idx, 0], offsets[idx, 1], offsets[idx, 2]]
                vertices.append(vertex)

        # Extend vertex_normals list
        vertex_normals.extend(np.repeat(face_normals, 3, axis=0).tolist())
    else:
        new_size = size / 3.0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    if (dx, dy, dz).count(0) < 2:
                        recurse(level - 1, x + dx * new_size, y + dy * new_size, z + dz * new_size, new_size, vertices, vertex_normals)
