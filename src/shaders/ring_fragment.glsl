#version 330

in vec3 frag_normal;
out vec4 fragColor;
uniform vec3 u_color;

void main() {
    float light = dot(normalize(frag_normal), vec3(0.0, 0.0, 1.0)) * 0.5 + 0.5;
    fragColor = vec4(u_color * light, 1.0);
}
