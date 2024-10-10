import numpy as np
cimport numpy as cnp

# Function to generate terrain using precomputed Perlin noise values
def generate_terrain(cnp.ndarray[cnp.float32_t, ndim=1] noise_values, int grid_size, float scale):
    cdef int half_grid = grid_size // 2
    cdef int i, j
    cdef int num_vertices = grid_size * grid_size
    cdef int num_indices = (grid_size - 1) * (grid_size - 1) * 6

    # Create memoryviews for better performance
    cdef cnp.ndarray[cnp.float32_t, ndim=2] vertices = np.empty((num_vertices, 3), dtype=np.float32)
    cdef cnp.ndarray[cnp.int32_t, ndim=1] indices = np.empty(num_indices, dtype=np.int32)
    cdef cnp.ndarray[cnp.float32_t, ndim=2] texcoords = np.empty((num_vertices, 2), dtype=np.float32)
    cdef cnp.ndarray[cnp.float32_t, ndim=2] normals = np.zeros((num_vertices, 3), dtype=np.float32)

    # Generate vertices and texture coordinates using precomputed noise values
    for i in range(grid_size):
        idx = i * grid_size  # Cache the row index
        for j in range(grid_size):
            vertex_index = idx + j
            vertices[vertex_index, 0] = (i - half_grid) * scale  # X
            vertices[vertex_index, 1] = noise_values[vertex_index]  # Y
            vertices[vertex_index, 2] = (j - half_grid) * scale  # Z
            texcoords[vertex_index, 0] = i / grid_size          # U
            texcoords[vertex_index, 1] = j / grid_size          # V

            # Generate indices for the vertex array in the same loop for better cache coherence
            if i < grid_size - 1 and j < grid_size - 1:
                base = (i * (grid_size - 1) + j) * 6
                top_left = vertex_index
                top_right = vertex_index + 1
                bottom_left = vertex_index + grid_size
                bottom_right = bottom_left + 1

                indices[base:base + 6] = np.array(
                    [top_left, bottom_left, top_right, top_right, bottom_left, bottom_right], dtype=np.int32)

    # Calculate normals
    for i in range(1, grid_size - 1):
        for j in range(1, grid_size - 1):
            current = i * grid_size + j
            left = (i - 1) * grid_size + j
            right = (i + 1) * grid_size + j
            up = i * grid_size + (j + 1)
            down = i * grid_size + (j - 1)

            # Calculate normal vector
            dx = vertices[right, 1] - vertices[left, 1]
            dz = vertices[up, 1] - vertices[down, 1]
            normal = np.array([-dx, 2.0, -dz], dtype=np.float32)
            normal /= np.linalg.norm(normal)  # Normalize the vector
            normals[current] = normal

    return vertices, indices, normals, texcoords
