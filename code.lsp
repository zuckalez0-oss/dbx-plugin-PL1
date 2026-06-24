(defun c:LIMPARPECAS ()
  (setvar "cmdecho" 0)
  
  ;; Garante que as camadas estão desbloqueadas antes de apagar
  (command "-layer" "U" "CONTORNO,DOBRAS,DOBRA" "")
  
  ;; Lista das camadas de peças que serão limpas
  (setq camadas '("CONTORNO" "DOBRAS" "DOBRA"))
  
  ;; Loop para varrer cada camada e apagar as entidades
  (foreach lay camadas
    (if (tblsearch "layer" lay)
      (progn
        (setq ss (ssget "X" (list (cons 8 lay))))
        (if ss
          (progn
            (command "erase" ss "")
            (princ (strcat "\nCamada " lay " limpa com sucesso."))
          )
          (princ (strcat "\nNenhum objeto encontrado na camada " lay "."))
        )
      )
      (princ (strcat "\nCamada " lay " nao existe no desenho atual."))
    )
  )
  
  (princ "\n[Sucesso] O arquivo padrao de pecas foi limpo!")
  (setvar "cmdecho" 1)
  (princ)
)