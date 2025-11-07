#version 330 core

layout (location =0) in vec3 vertexPos;
layout (location =1) in vec3 vertexNormal;

out vec3 TexCoords;

uniform mat4 view;
uniform mat4 projection;

void main()
{
    TexCoords = vertexPos;
    vec4 pos = projection * view * vec4(vertexPos, 1.0);
    gl_Position = pos.xyww;
}