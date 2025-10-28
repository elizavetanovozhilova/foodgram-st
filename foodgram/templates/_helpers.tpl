{{- define "foodgram.labels" -}}
app.kubernetes.io/name: "{{ include "foodgram.name" . }}"
app.kubernetes.io/instance: "{{ .Release.Name }}"
app.kubernetes.io/version: "{{ .Chart.AppVersion }}"
app.kubernetes.io/managed-by: "{{ .Release.Service }}"
{{- end -}}

{{- define "foodgram.name" -}}
{{ .Chart.Name }}
{{- end }}

{{- define "foodgram.fullname" -}}
{{ include "foodgram.name" . }}
{{- end }}

{{- define "foodgram.chart" -}}
{{ .Chart.Name }}-{{ .Chart.Version }}
{{- end }}

