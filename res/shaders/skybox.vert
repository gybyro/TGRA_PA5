#version 330 core

// struct INPUT {

// }

layout (location= 0) in vec3 vertexPos;
layout (location= 1) in vec2 vertexTexCoord;
layout (location= 2) in vec3 vertexNormal;

uniform mat4 view;
uniform mat4 projection;

// out vec2 fragmentTexCoord;
// out vec3 fragmentPosition;
// out vec3 fragmentNormal;


out vec3 TexCoords;

void main()
{
    TexCoords = vertexPos;
    vec4 pos = projection * view * vec4(vertexPos, 1.0);
    gl_Position = pos.xyww;
}