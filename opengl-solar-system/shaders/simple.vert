#version 330 core

in vec3 position;
in vec2 texCoord;
in vec3 normal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform float cloudOffset;

out vec3 fragPos;
out vec3 fragNormal;
out vec2 fragTexCoord;
out vec2 fragCloudCoord;

void main()
{
    vec4 worldPos = model * vec4(position, 1.0);
    fragPos = vec3(worldPos);
    fragNormal = mat3(transpose(inverse(model))) * normal;
    fragTexCoord = texCoord;
    fragCloudCoord = texCoord + vec2(cloudOffset, 0.0);
    gl_Position = projection * view * worldPos;
}
