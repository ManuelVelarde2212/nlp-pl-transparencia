#upload
#install.packages("tm")
#install.packages("qdap")
#install.packages("openNLP")
library(tm)
library(qdap)
require(openNLP)

# Lectura de Archivo
c <- Corpus(DirSource("Aquí va la dirección de su archivo"))
summary(c)

# Creación de matriz tf-idf
# dtm <- DocumentTermMatrix(c, control=list(wordLengths=c(3,Inf),weighting = weightTfIdf))
dtm <- DocumentTermMatrix(c)
x<-as.matrix(dtm)
rownames(x) <- paste(substring(rownames(x),1,5))

# Distancia
m <- as.matrix(dist(x))
d <- as.dist(m)
stopifnot(d == dist(x))


# Archivo para guardar la matriz de términos de documento
write.csv(x,file="dtm-Transparencia.csv")

# Dendograma
groups <- hclust(d,method="ward.D")
plot(groups, hang=-1)
rect.hclust(groups,2)

# Clustering
# Algoritmo kmeans, 2 clusters, configuración inicial = 100
kfit <- kmeans(d, 2, nstart=100)
library(cluster)
clusplot(m, kfit$cluster, color=T, shade=T, labels=2, lines=0)


# Hallar el número óptimo de clusters
m.scaled<-scale(x)
k.max <- 15
data <- m.scaled
sil <- rep(0, k.max)
# Calcular el ancho de silueta promedio para 
# k = 2 a k = 5
for(i in 2:k.max){
  km.res <- kmeans(data, centers = i, nstart = 25, iter.max=30)
  ss <- silhouette(km.res$cluster, dist(data))
  sil[i] <- mean(ss[, 3])
}

# Mostrar el ancho de silueta promedio
plot(1:k.max, sil, type = "b", pch = 19, 
     frame = FALSE, xlab = "Número de clusters k")
abline(v = which.max(sil), lty = 2)