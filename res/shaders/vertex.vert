#version 330 core

layout (location=0) in vec3 vertexPos;
layout (location=1) in vec2 vertexTexCoord;
layout (location = 2) in vec3 vertexNormal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

uniform bool uIsBillboard; // buh

uniform vec2 uTexRepeat;  // passed from RepeatingMaterial

out vec2 fragmentTexCoord;
out vec3 fragmentPosition;
out vec3 fragmentNormal;

void main()
{
    vec4 worldPos = model * vec4(vertexPos, 1.0);
    fragmentPosition = worldPos.xyz;

    // Properly transform normal by inverse-transpose of model matrix
    // fragmentNormal = mat3(transpose(inverse(model))) * vertexNormal;

    // Use a fixed facing normal for billboards to avoid lighting drift as they rotate
    if (uIsBillboard) {
        fragmentNormal = vec3(0.0, 0.0, 1.0);
    } else {
        // Properly transform normal by inverse-transpose of model matrix
        fragmentNormal = mat3(transpose(inverse(model))) * vertexNormal;
    }

    fragmentNormal = normalize(fragmentNormal);

    fragmentTexCoord = vertexTexCoord * uTexRepeat; // repeated textures
    gl_Position = projection * view * worldPos;

}
