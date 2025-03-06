#version 330

in vec3 in_position;
in vec3 in_normal;
uniform mat4 model;
uniform mat4 projection;

out vec3 frag_normal;

void main() {
    gl_Position = projection * model * vec4(in_position, 1.0);
    frag_normal = normalize(mat3(model) * in_normal);
}
