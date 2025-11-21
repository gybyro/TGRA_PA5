#version 330 core

in vec3 TexCoords;
out vec4 FragColor;

uniform samplerCube uSkyboxA;
uniform samplerCube uSkyboxB;
uniform float uMix; // 0.0 = skyboxA, 1.0 = skyboxB

void main()
{
    vec3 dir = normalize(TexCoords);
    vec4 colorA = texture(uSkyboxA, dir);
    vec4 colorB = texture(uSkyboxB, dir);
    FragColor = mix(colorA, colorB, uMix);
}